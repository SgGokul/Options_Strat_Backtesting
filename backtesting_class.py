import pandas as pd
from tqdm import tqdm
from data_processing import groupby_options
from bnf_ohlcv_data import bnf_data


class backtesting:
    ## input all class parameters
    def __init__(self, filepath_fut, filepath_opt, capital, wing_percent, sl, tp):
        self.filepath_fut = filepath_fut
        self.filepath_opt = filepath_opt
        self.wing_percent = wing_percent
        self.sl = sl
        self.tp = tp
        self.get_fut_ohlcv_data()
        self.get_opt_ohlcv_data()
        self.tradebook = pd.DataFrame(columns = ['Date', 'Expiry', 'CE_short_en_date', 'PE_short_en_date', 
                                                 'CE_long_en_date', 'PE_long_en_date', 'CE_short_ex_date', 'PE_short_ex_date',
                                                 'CE_long_ex_date', 'PE_long_ex_date', 'Fut_En_price', 'ATM_stk',
                                                 'CE_short_stk', 'PE_short_stk', 'CE_long_stk', 'PE_long_stk',
                                                 'CE_short_en_price', 'PE_short_en_price', 'CE_long_en_price',
                                                 'PE_long_en_price', 'CE_short_ex_price', 'PE_short_ex_price',
                                                 'CE_long_ex_price', 'PE_long_ex_price', 'TP/SL/SqOFF'])
    
    ## get the banknifty future ohlcv data by calling the bnf_ohlcv_data.py file
    def get_fut_ohlcv_data(self):
        raw = pd.read_csv(self.filepath_fut)
        self.bnf_data = bnf_data(raw)
        
    
    ## get the banknifty options ohlcv data of all strikes and diff types of contracts 
    ## in a dict format by calling data_processing.py file
    def get_opt_ohlcv_data(self):
        raw = pd.read_csv(self.filepath_opt)
        self.options_dict, self.expiry_list = groupby_options(raw)
        
    
    ## calculate the strike price of the contract for entry    
    def stk_price(self, spot_price):
        stk = (round(spot_price/100))*100
        
        return stk 
    
    ## calculate the strike prices of the contracts for entry of wings
    def wing_stk(self, stk):
        wing_ce_stk = self.stk_price(stk*(1+self.wing_percent))
        wing_pe_stk = self.stk_price(stk*(1-self.wing_percent))
        
        return wing_ce_stk, wing_pe_stk
    
    ## extract key from the dictionary for CE and PE contracts for short ATM Straddle
    def strike_key(self, nearest_expiry, stk):
        search_str = "BANKNIFTY_" + str(nearest_expiry) + "_" + str(stk)
                            
        ce_key = None
        pe_key = None
        for key in self.options_dict.keys():
            if search_str + ".0_CE" in key:
                ce_key = key
            elif search_str + ".0_PE" in key:
                pe_key = key
            if ce_key and pe_key:
                break
            
        return ce_key, pe_key
    
    ## extract key from the dictionary of different contracts for the wing trades that we take for protection
    def wing_key(self, nearest_expiry, stk, type):
        search_str = "BANKNIFTY_" + str(nearest_expiry) + "_" + str(stk)
        
        contract_key = None
        for key in self.options_dict.keys():
            if search_str + ".0_" + type in key:
                contract_key = key
            if contract_key:
                break
        
        return contract_key   
    
    ## extract premium during the time of entry/exit
    def opt_premium(self, key, date, ohlc):
        premium = self.options_dict[key][self.options_dict[key]['Datetime'] == date][ohlc].iloc[0]     
    
        return premium
    
    ## extract the nearest premium avail or the premium avail at a specified timestamp
    def get_nearest_premium_value(self, key, date, ohlc):
        if date in self.options_dict[key]['Datetime'].values:
            return self.opt_premium(key, date, ohlc), date
        else:
            data = self.options_dict[key]
            nearest_data_index = data[data['Datetime'] > date].index.min()
            if pd.isna(nearest_data_index):  
                nearest_data_index = (data['Datetime'] - date).abs().idxmin()
            
        return data.loc[nearest_data_index, ohlc], data.loc[nearest_data_index, 'Datetime']
    
    
    ## update tradebook accordingly with exit prices and exit times 
    def update_tradebook(self, tradecheck, exit_date, ce_key, pe_key, wing_ce_key, wing_pe_key):
        wing_ce_premium_value, wing_ce_exit_date = self.get_nearest_premium_value(wing_ce_key, exit_date, 'Close')
        wing_pe_premium_value, wing_pe_exit_date = self.get_nearest_premium_value(wing_pe_key, exit_date, 'Close')
        ce_premium_value, ce_exit_date = self.get_nearest_premium_value(ce_key, exit_date, 'Close')
        pe_premium_value, pe_exit_date = self.get_nearest_premium_value(pe_key, exit_date, 'Close')
        self.tradebook.loc[tradecheck, 'CE_short_ex_price'] = ce_premium_value
        self.tradebook.loc[tradecheck, 'CE_short_ex_date'] = ce_exit_date
        self.tradebook.loc[tradecheck, 'PE_short_ex_price'] = pe_premium_value
        self.tradebook.loc[tradecheck, 'PE_short_ex_date'] = pe_exit_date
        self.tradebook.loc[tradecheck, 'CE_long_ex_price'] = wing_ce_premium_value
        self.tradebook.loc[tradecheck, 'CE_long_ex_date'] = wing_ce_exit_date
        self.tradebook.loc[tradecheck, 'PE_long_ex_price'] = wing_pe_premium_value
        self.tradebook.loc[tradecheck, 'PE_long_ex_date'] = wing_pe_exit_date    
    
    ## backtest the strategy here generating trading logs alongside    
    def test_strat(self):
        date = pd.to_datetime(self.bnf_data['Datetime'].iloc[0])
        end_date = pd.to_datetime(self.bnf_data['Datetime'].iloc[-1])
        tp_hit = False
        sl_hit = False
        tradecheck = 1

        with tqdm(total=(end_date - date).total_seconds() / 60) as pbar:
            ## backtesting from start date till end date avail
            while date <= end_date:
                ## try and except to bypass missing values
                try:
                    ## entry during 10.30 a.m.
                    if date.strftime("%H:%M") == "10:29":
                        ## try and except to execute trades only during trading days
                        try:
                            ## calculate strike prices of straddle to enter at
                            fut_en_price = self.bnf_data[self.bnf_data['Datetime'] == date]['Close'].iloc[0]
                            stk = self.stk_price(fut_en_price)
                            
                            ## get the nearest expiry day
                            nearest_expiry = min(filter(lambda x: pd.to_datetime(x) >= pd.Timestamp(date.date()), self.expiry_list))
                            
                            ## calculate strike price of the wings to enter at 
                            wing_ce_stk, wing_pe_stk = self.wing_stk(stk)
                            
                            ce_key, pe_key = self.strike_key(nearest_expiry, stk)
                            wing_ce_key = self.wing_key(nearest_expiry, wing_ce_stk, "CE")
                            wing_pe_key = self.wing_key(nearest_expiry, wing_pe_stk, "PE")
                            
                            ## extract entry prices and entry time of different contracts to enter at
                            entry_date = date + pd.Timedelta(minutes=1)
                            ce_entry, ce_entry_time = self.get_nearest_premium_value(ce_key, entry_date, 'Open')
                            pe_entry, pe_entry_time = self.get_nearest_premium_value(pe_key, entry_date, 'Open')
                            wing_ce_entry, wing_ce_entry_time = self.get_nearest_premium_value(wing_ce_key, entry_date, 'Open')
                            wing_pe_entry, wing_pe_entry_time = self.get_nearest_premium_value(wing_pe_key, entry_date, 'Open')
                            
                            ## lock in the values of entry prices and time into the tradebook
                            self.tradebook.loc[tradecheck] = [entry_date.date(), nearest_expiry, ce_entry_time,
                                                              pe_entry_time, wing_ce_entry_time, wing_pe_entry_time, 0, 0, 0,   
                                                              0, fut_en_price, stk, stk, stk, wing_ce_stk, wing_pe_stk, 
                                                              ce_entry, pe_entry, wing_ce_entry, wing_pe_entry, 0, 0, 0, 0, 'SqOFF']
                            
                            ## calculate take profit and stop loss
                            tp_premium_value = (ce_entry + pe_entry)*(1 - self.tp)
                            sl_premium_value = (ce_entry + pe_entry)*(1 + self.sl)
                            
                            ## loop to check for exit condition
                            while entry_date.strftime("%H:%M") <= "15:19":
                                
                                ## check for data avail or not
                                ce_data_available = entry_date in self.options_dict[ce_key]['Datetime'].values
                                pe_data_available = entry_date in self.options_dict[pe_key]['Datetime'].values
                                
                                if not ce_data_available or not pe_data_available:
                                    entry_date = entry_date + pd.Timedelta(minutes=1)
                                    continue
                                
                                ## calculate the premium sum to check for exit condition
                                short_ce_premium_value = self.opt_premium(ce_key, entry_date, 'Close')
                                short_pe_premium_value = self.opt_premium(pe_key, entry_date, 'Close')
                                premium_sum = short_ce_premium_value + short_pe_premium_value
                                
                                ## check for tp condition being breached
                                if tp_premium_value >= premium_sum:
                                    exit_date = entry_date
                                    tp_hit = True
                                    
                                    self.update_tradebook(tradecheck, exit_date, ce_key, pe_key, wing_ce_key, wing_pe_key)
                                    
                                    
                                    self.tradebook.loc[tradecheck, 'TP/SL/SqOFF'] = 'TP'
                                    tradecheck += 1
                                    break
                                
                                ## check for sl condition being breached
                                if sl_premium_value <= premium_sum:
                                    exit_date = entry_date
                                    sl_hit = True
                                    
                                    self.update_tradebook(tradecheck, exit_date, ce_key, pe_key, wing_ce_key, wing_pe_key)
                                    
                                    self.tradebook.loc[tradecheck, 'TP/SL/SqOFF'] = 'SL'
                                    tradecheck += 1
                                    break    
                                
                                entry_date = entry_date + pd.Timedelta(minutes=1)
                            
                            ## if neither tp nor sl hit, square off position    
                            if (tp_hit == False) and (sl_hit == False):
                                exit_date = entry_date
                                
                                self.update_tradebook(tradecheck, exit_date, ce_key, pe_key, wing_ce_key, wing_pe_key)

                                tradecheck += 1
                            else : 
                                tp_hit = False
                                sl_hit = False    
                            
                        except IndexError:
                            date = date + pd.Timedelta(minutes=1)
                            continue
                        
                    date = date + pd.Timedelta(minutes=1)
                except KeyError:
                    date = date + pd.Timedelta(minutes=1)
                    continue
                pbar.update(1)   
                   
        df = self.tradebook
        
        ## returns tradebook
        return df