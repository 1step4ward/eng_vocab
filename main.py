import gradio as gr
# import altair as alt
# from vega_datasets import data # demo
import engword as ew

class CheckSession:
    limit_count = 30
    current_count = 0
    current_word_index = 0
    number_correct_answer = 0
    is_start = False
    
    def __init__(self, word_list: ew.WordList) -> None:
        self.wl = word_list
        return
    
    def start(self) -> None:
        if self.is_start:
            return
        
        self.target_words = self.wl.get_target_words()
        self.current_word_index = 0
        self.number_correct_answer = 0
        self.is_start = True
        return
    
    def stop(self) -> None:
        if not self.is_start:
            return
        
        self.is_start = False

        return
    
    def count(self) -> None:
        if not self.is_start:
            return
        
        self.current_count += 1

        if self.current_count > self.limit_count:
            self.wl.update_word(self.target_words.iloc[self.current_word_index]['word'], False)

            self.current_word_index += 1
            self.current_count = 0
            if self.current_word_index >= len(self.target_words):
                self.is_start = False

        return
    
    def get_progress(self) -> str:
        return str(self.current_word_index + 1) + " / " + str(len(self.target_words)) + " : " + str(self.number_correct_answer) + " correct"
    
    def get_count(self) -> str:
        return str(self.current_count) + " / " + str(self.limit_count) + " seconds"
    
    def reset_count(self) -> None:
        self.current_count = 0
        return
    
    def get_question(self) -> str:
        if self.current_word_index < len(self.target_words):
            return self.target_words.iloc[self.current_word_index]['question']
        else:
            return ""

    def answer(self, answer_word: str) -> str:
        print("answer button pressed")
        if not self.is_start:
            return ""
        
        if self.target_words.iloc[self.current_word_index]['word'] == answer_word:
            self.wl.update_word(self.target_words.iloc[self.current_word_index]['word'], True)

            self.number_correct_answer += 1
            self.current_word_index += 1
            self.current_count = 0

            if self.current_word_index >= len(self.target_words):
                self.is_start = False

            return "correct!"
        else:
            return "wrong..."

wl = ew.WordList('test.json')
cs = CheckSession(wl)

def display_overall():
    return [wl.get_num_total_words(), wl.get_num_memorized_words(), wl.get_num_target_words()]

def check_start():
    cs.start()
    return

def check_cycle():
    cs.count()
    return [cs.get_progress(), cs.get_count(), cs.get_question()]

def check_stop():
    cs.reset_count()
    return [cs.get_progress(), cs.get_count(), cs.get_question()]

def check_answer(answer_text: str):
    result = cs.answer(answer_text)
    return [cs.get_progress(), cs.get_count(), cs.get_question(), result]
        

# UI
with gr.Blocks() as demo:

    gr.Markdown("# Want New Vocabulary")
    with gr.Tab("Overall"):
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("")
                num_reg_words = gr.Textbox(label="Registered words: ")
                num_mem_words = gr.Textbox(label="Memorized words: ")
                num_check_words = gr.Textbox(label="Words to check: ")
            with gr.Column(scale=2):
                gr.Markdown("")

        with gr.Accordion("■ Register new word.", open=False):
            new_word = gr.Textbox()
            add_button = gr.Button("Add")
                
    with gr.Tab("Check"):
        gr.Markdown("Check words.")
        with gr.Row():
            start_button = gr.Button("Start")
            stop_button = gr.Button("Stop")
        with gr.Row():
            progress_text = gr.Textbox(label="Progress")
            countdown_text = gr.Textbox(label="Time Limit")
        with gr.Row():
            question_text = gr.Textbox(label="Question")
        with gr.Row():
            answer_word = gr.Textbox()
            answer_button = gr.Button("Answer")
    
    # Event
    demo.load(display_overall, None, [num_reg_words, num_mem_words, num_check_words])
    add_button.click(fn=wl.add_word, inputs=new_word, outputs=new_word).then(display_overall, None, [num_reg_words, num_mem_words, num_check_words])
    answer_button.click(check_answer, answer_word, [progress_text, countdown_text, question_text, answer_word])
    st = start_button.click(check_start, None, None).then(check_cycle, None, [progress_text, countdown_text, question_text], every=1)
    stop_button.click(check_stop, None, [progress_text, countdown_text, question_text], cancels=[st])
    
# Web UI launch
demo.queue().launch(inbrowser=True)
wl.save_json()