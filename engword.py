import pandas as pd
import os
from datetime import datetime
from dotenv import load_dotenv

from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

class WordList:
    columns = ['word', 'registered_date', 'last_answered_date', 'question', 'result', 'false_count', 'level']

    def __init__(self, json_name: str) -> None:
        # Load the word list
        # Check if json_name exists or not
        self.json_name = json_name
        if os.path.isfile(self.json_name):
            self.df = pd.read_json(json_name)
        else:
            self.df = pd.DataFrame(index=[], columns=self.columns)
        
        # Question generator
        self.qg = QGen()

        return
    
    def save_json(self) -> None:
        self.df.to_json(self.json_name)
        return
    
    def add_word(self, word: str):
        if len(self.df[self.df['word'] == word]):
            return "Failed"
        else:
            record = pd.Series([word, datetime.now().strftime('%Y/%m/%d %H:%M:%S.%f'), datetime.now().strftime('%Y/%m/%d %H:%M:%S.%f'), self.qg.generate_question(word), True, 0, 0], index=self.columns)
            self.df.loc[str(len(self.df))] = record
            self.save_json()
            return "OK"

    def delete_word(self, word: str):
        if len(self.df[self.df['word'] == word]):
            self.df = self.df[self.df['word'] != word]
            self.df.reset_index(inplace=True, drop=True)
            return True
        else:
            return False

    def get_num_total_words(self):
        return len(self.df.groupby('word'))
    
    def get_num_memorized_words(self):
        return len(self.df[self.df['level'] == 6])
    
    def get_memorizing_level(self, word: str):
        # Level duration
        #     0     init
        #     1     1day
        #     2    3days
        #     3    1week
        #     4   1month
        #     5  +1month
        #     6 memorized
        return self._get_word_attribute(word, 'level')
    
    def reset_memorizing_level(self, word: str):
        return self._update_word_attribute(word, 'level', 0)

    def _get_word_attribute(self, word: str, attr: str):
        target_df = self.df[self.df['word'] == word]
        if len(target_df):
            return target_df.iloc[0][attr]
        else:
            return word
    
    def _update_word_attribute(self, word: str, attr: str, value):
        target_df = self.df[self.df['word'] == word]
        if len(target_df):
            self.df.loc[self.df['word'] == word, attr] = value
            return True
        else:
            return False

    def get_target_words(self):
        def get_time_diff_threshold(level):
            time_diff_threshold = [
                "0 days 00:00:00.000000",
                "1 days 00:00:00.000000",
                "3 days 00:00:00.000000",
                "7 days 00:00:00.000000",
                "30 days 00:00:00.000000",
                "30 days 00:00:00.000000",
                "0 days 00:00:00.000000",
            ]
            if level <= 6:
                return time_diff_threshold[level]
            else:
                return time_diff_threshold[0]
            
        target_df = self.df.copy()
        
        current_time = datetime.now()
        target_df['time_diff'] = current_time - pd.to_datetime(target_df['last_answered_date'])
        target_df['time_diff_threshold'] = target_df['level'].map(get_time_diff_threshold)
        target_df = target_df[target_df['time_diff'] >= target_df['time_diff_threshold']]

        # print(target_df)
        return target_df

    def get_num_target_words(self):
        target_df = self.get_target_words()
        return len(target_df)
    
    def update_word(self, word: str, is_correct: bool):
        result = self._get_word_attribute(word, 'result')
        if result == word:
            return False
        
        self._update_word_attribute(word, 'last_answered_date', datetime.now().strftime('%Y/%m/%d %H:%M:%S.%f'))
        self._update_word_attribute(word, 'result', is_correct)
        if result:
            if is_correct:
                level = int(self.get_memorizing_level(word)) + 1
                self._update_word_attribute(word, 'level', level)
                self._update_word_attribute(word, 'question', self.qg.generate_question(word))
            else:
                self._update_word_attribute(word, 'false_count', 1)
        else:
            if is_correct:
                self._update_word_attribute(word, 'false_count', 0)
            else:
                false_count = int(self._get_word_attribute(word, 'false_count')) + 1
                if false_count >= 3:
                    level = int(self.get_memorizing_level(word))
                    if level > 0:
                        self._update_word_attribute(word, 'level', level - 1)
                        self._update_word_attribute(word, 'false_count', 0)
                    else:
                        self._update_word_attribute(word, 'false_count', false_count)
                else:
                    self._update_word_attribute(word, 'false_count', false_count)
        return True
    
class QGen:
    def __init__(self) -> None:
        load_dotenv()
        self.llm = OpenAI(temperature=0.9)
        self.prompt = PromptTemplate(
            input_variables=["word"],
            template="Can you create a sentence using {word} in 15 words?",
        )
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)
        return
    
    def generate_question(self, word: str):
        sentence = self.chain.run(word)
        replacement = '*' * len(word)
        sentence = sentence.replace(word, replacement)
        sentence = sentence.replace('\n', '')
        return sentence
    