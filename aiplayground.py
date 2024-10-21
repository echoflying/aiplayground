import streamlit as st

import _difflines as df    # type: ignore
import _aichat as ai

# global environment store into st.session_state
# set a easy way to access
class Env():
    # save all your variables inside st.session_state
    def __init__(self):
        if not self.has("working_step"):
            st.session_state.working_step = 1
        if not self.has("show"):
            st.session_state.show = Show()
        if not self.has("app"):
            st.session_state.app = App()
 
    def __getattr__(self, key):
        if key not in st.session_state:
            raise AttributeError(f"Invalid access to st.session_state, key = {key}")
        else:
            return st.session_state[key]

    def __setattr__(self, key, value):
        st.session_state[key] = value

    def __getitem__(self, key):
        if key not in st.session_state:
            raise AttributeError(f"Invalid access to st.session_state, key = {key}")
        else:
            return st.session_state[key]

    def __setitem__(self, key, value):
        st.session_state[key] = value

    def __len__(self, key):
        return len(st.session_state[key])

    def has(self, key):
        if key not in st.session_state:
            return False
        else:
            return True
        

# manage all layout
class Show():
    _canvas = None
    _answer_area = None
    cols = []            # for step4
    col0_html = []       # html catch
    current_line = 0

    def __init__(self):
        st.set_page_config(
            page_title="AI playground",
            page_icon="🧊",
            layout="wide",
        )
        self._canvas = st.empty()
        self._default_prompt = """
<角色>
你是一名精通中医中药的专业人员，精通中医经典，熟练掌握中医术语、中药名称、方剂名称等。

<任务>
你将根据要求校对用户提供的文字，文字的内容是中医的中药学、伤寒论、针灸等课程课程录音的文字稿。

<要求>
- 根据上下文校对可能因为语音识别错误导致的断句错误、文字错误和错别字。
- 去除非必须的语气词，如“嗯”、“啊”、“然后”、“这个”等。
- 如有语句不通顺的地方，判断是否包含可能的断句错误并纠正
- 语音识别导致的错误示例："当森"应为"党参"，"党生"应为"党参"，"浮南"应为"湖南"

<限制>
- 不做任何用词的改写和润色，如用正式词语替换口语话的文字等。
- 不做任何句子的改写和润色。
- 维持原有的格式，不省略任何信息。
- 【重要】不要删除任何内容
- 不要删除文本中的空行
- 保留文本中出现的时间标志
- 仅输出校对后的文字，不作任何其他说明
"""

    def run(self):
        # you may use string for more meaningful reference
        if env.working_step == 1:
            self.show_step1()
        elif env.working_step == 2:
            self.show_step2()
        elif env.working_step == 3:
            self.show_step3()
        elif env.working_step == 31:
            self.show_step31()
        elif env.working_step == 311:
            self.show_step311()
        elif env.working_step == 4:
            self.show_step4()
        elif env.working_step == 5:
            self.show_step5()
        else:
            raise ValueError(f"{env.working_step}")
        

    # start, get passcode
    def show_step1(self):
        self._canvas.empty()
        cav = self._canvas.container(border = True)
        info = ("This application is for play and testing AI.\n"
               "Zhipuai LLM model [glm-4-flash] is used as default LLM.\n"
               "Optional passkey will alow you to select more model for testing.")
        cav.subheader("Ai playground ...")
        cav.text(info)

        text = cav.text_input(label = "input passkey if you have, leave blank if you don't", 
                              value="")
        if text:
            env.app.set_passkey(text)
        # other way to pass the input value is by st.session_state.key_str, which break the way we encapsulate the environment

        cav.button("Go Next step", on_click=env.app.on_click1)

    def show_step2(self):
        self._canvas.empty()
        cav = self._canvas.container()
        cav.subheader("Input LLM prompt and text")

        # show LLM model select list if got right passkey  
        pr = ""
        if env.app.passkey_ok():
            m = cav.selectbox("Select LLM", env.app.model_list, 0, )
            env.app.set_model(m)
            pr = self._default_prompt      # default prompt loaded if passkey ok

        # show prompt and text edit area
        p1 = cav.expander("Prompt")
        prompt = p1.text_area(label = "Input your prompt", 
                            value = pr, 
                            height = 300)
        if prompt:
            env.app.set_prompt(prompt)

        p2 = cav.expander("User Text")
        t = env.app.get_text() if env.app.recook else ""       # answer already set to text as recook requested
        label = f"Input user text: [{env.app.text_name}]" if env.app.recook else "Input user text"
        text = p2.text_area(label = label, 
                            value = t, 
                            height = 300,)
        if text:                                               # got text
            env.app.set_text(text)

        cav.button("Start run LLM", on_click=env.app.on_click2)
        # for debug
        cav.write(env.app.text_lists)

    # just clear the canvas
    def show_step3(self):
        self._canvas.empty()
        env.working_step = 31
        st.rerun()

    # run AI and show answer
    def show_step31(self):
        self._canvas.empty()
        cav = self._canvas.container()
        cav.subheader("Answer")

        # run AI
        self._answer_area = cav.expander("Answer", expanded = True)
        #env.app._answer = self._answer_area.write_stream(env.app.run_llm_stream)
        env.app._answer = env.app._text  # debug only
        # save answer
        t = env.app._answer.split("\n")
        lines = [s for s in t if s.strip()!= ""]    # remove blank line
        env.app.answer_name = env.app.text_name+"+"+ env.app.model.model
        env.app.text_lists.append([env.app.answer_name, lines])

        # show diff if needed
        if env.app.passkey_ok():
            # prepare to show diff
            aa = env.app.get_text().split("\n")
            bb = env.app.get_answer().split("\n")

            # should remove empty line
            aa = [s for s in aa if s.strip()]
            bb = [s for s in bb if s.strip()]
            diff_ab = df.diff_lines(aa, bb)
            env.app.op_list = df.combine_changed_lines(aa, bb, diff_ab)

            i = 0
            s = ""
            for l in env.app.op_list:  # layout delete and insert
                s = s + df.change_oneline_to_html(l, i == 0)
                s = s + "<br/><br/>"
                i += 1
            p2 = cav.expander(f"difference[{env.app.text_name} : {env.app.answer_name}]")
            p2.html(s)

        if env.app.passkey_ok():
            col1, col2, col3 = cav.columns(3)
            col1.button("Finish, we go back", on_click=env.app.on_click31a)    # go 2
            col2.button("Back with new text", on_click = env.app.on_click31b) # go 311
            col3.button("Edit manually", on_click = env.app.on_click31c_4)      # go 4
        else:
            cav.button("Finish, we go back", on_click=env.app.on_click31a)     # go 2


    # select recook item
    def show_step311(self):
        self._canvas.empty()
        cav = self._canvas.container()
        cav.subheader("Select recook batch")

        # select recook 
        name_list = [item[0] for item in env.app.text_lists]
        name = cav.selectbox("Select text want recook", name_list, 0, )

        cav.button("go recook", on_click = env.app.on_click311_2, args = (name,))


    def show_step4(self):
        self._canvas.empty()
        cav = self._canvas.container(border = True)
        cav.subheader("Manual edit")

        line_num = len(env.app.op_list)
        start_line = None
        end_line = None
        if line_num < 10:
            start_line = 0
            end_line = line_num -1
        elif self.current_line < 3:
            start_line = 0
            end_line = 9
        elif self.current_line + 6 > line_num:
            end_line = line_num -1
            start_line = end_line - 9
        else:
            start_line = self.current_line -3
            end_line = self.current_line + 6
        
        # show all lines
        self.cols = []
        i = 0
        while start_line + i <= end_line:
            self.cols.append([None, None, None])
            self.cols[i][0], self.cols[i][1], self.cols[i][2] = cav.columns([9,2,9])

            ii = start_line + i
            self.cols[i][0].html(self.col0_html[ii])
            self.cols[i][1].button("OK", key = f"b{ii}")
            ca = self.cols[i][2].text_area(
                                    "edit", env.app.c_list[ii], height = 300,
                                    key = f"t{ii}",
                                    label_visibility = "collapsed")
 
            if ca != env.app.c_list[ii]:  # text changed
                env.app.c_list[ii] = ca
 
                # update op_list and html of that line
                l = None
                if env.app.o_list[ii] == env.app.c_list[ii]:
                    l = ["e",env.app.o_list[ii], None]
                else:
                    line_op = df.diff_str(env.app.o_list[ii], env.app.c_list[ii])
                    l = ["s",env.app.o_list[ii] +"\n" + env.app.c_list[ii], line_op]
                env.app.op_list[ii] =l
                self.col0_html[ii] = df.change_oneline_to_html(l)   # cache all html
                self.current_line = ii

                st.rerun()
 
            i += 1
            cav.write("---")

        cav.button("Final, go get the result", on_click=env.app.on_click4_5)

    def show_step5(self):
        self._canvas.empty()
        cav = self._canvas.container(border = True)
        cav.subheader("All done")

        s = "\n\n".join(env.app.c_list)
        cav.text_area("Copy the text to your local file", s)

        cav.button("Back to manual edit", on_click=env.app.on_click5_4)


# end of class Show


class App():

    def __init__(self):
        self._passkey = ""
        self._prompt = ""
        self._text = ""
        self.text_name = ""     # eg. origin, origin+glm-4-flash, origin+glm-4-flash+doubao32
        self._answer = ""
        self.answer_name = ""
        self.model = ai.AI_models()
        self.model_list = self.model.get_model_list()
        self.op_list = []
        self._ai_client = None
        self.recook = False
        self.text_lists = []    # ai refined list, {ai_model_name, list}, eg.: origin; origin+glm-4-flash;original+glm-4-flash+doubao32
        self.o_list = []        # origin list: save user origin text
        self.i_list = []        # index list: compare origin and candidate
        self.c_list = []        # candidate list: select one as candidate, for edit

    def set_passkey(self, k):
        self._passkey = k
        
    def passkey_ok(self):
        return self._passkey == st.secrets.app.passkey

    def set_prompt(self, p):
        self._prompt = p

    def get_prompt(self):
        return self._prompt

    def set_text(self, t):
        self._text = t

    def get_text(self):
        return self._text

    def set_model(self, m):
        self.model.set_model(m)

    def get_answer(self):
        return self._answer

    def run_llm_stream(self):
        self._ai_client = ai.LLM_ai(self.model.llm, self.model.model, self.model.max_tokens)

        # split article to paragraphs less than MAX_AI_PARA_LEN
        MAX_AI_PARA_LEN = 2000  # max length pass to AI
        paragraphs = []
        current_paragraph = ""
        for line in self._text.split('\n'):             # skip blank line but add "\n\n" at the end of line
            if line == "":    # skip blank line
                continue
            if len(current_paragraph) + len(line) > MAX_AI_PARA_LEN:
                paragraphs.append(current_paragraph)
                current_paragraph = line + "\n\n"        # here new line start
            else:
                current_paragraph += line + "\n\n"
        
        if current_paragraph:                          # end of the file, merge the rest
            paragraphs.append(current_paragraph)
            
        for para in paragraphs:
            # print("START: prompt ==[", self._prompt, "]==text ==[", para, "]==END")
            yield from self._ai_client.chat_stream(self._prompt, para)


    def on_click1(self):
        # goto next step 
        env.working_step = 2
    
    def on_click2(self):
        @st.dialog("Error: empty data ...")
        def error_empty_text():
            st.warning("Should input something for AI to deal with.", icon = "⚠️")
            if st.button("OK"):
                st.rerun()

        # stay step 2 if no text input
        if self._text is None or self._text == "":
            error_empty_text()
            st.rerun()

        # with text, go next step
        if not self.recook:
            o1 = self._text.split("\n")
            self.o_list = [s for s in o1 if s.strip()!= ""]    # remove blank line
            self.text_lists = [["origin", self.o_list]]
            self.text_name = "origin"
        else:
            pass



        env.working_step = 3


    # go back
    def on_click31a(self):
        self._text = ""
        self.text_name = "origin"
        self.recook = False
        env.working_step = 2

    # recook
    def on_click31b(self):
        env.working_step = 311   # go select recook item

    def on_click31c_4(self):
        if not env.app.c_list:      # initiate c_list 
            env.app.c_list = env.app.text_lists[-1][1]

        # make diff of lines, no delete/insert
        self.op_list = []  # clear used op_list in step 2
        i = 0
        while i < len(env.app.o_list):
            line = None
            if env.app.o_list[i] == env.app.c_list[i]:
                line = ["e",env.app.o_list[i], None]
                env.app.op_list.append(line)
            else:
                line_op = df.diff_str(env.app.o_list[i], env.app.c_list[i])
                line = ["s",env.app.o_list[i] +"\n" + env.app.c_list[i], line_op]
                env.app.op_list.append(line)
            env.show.col0_html.append(df.change_oneline_to_html(line))   # cache all html
            i += 1

        env.show.current_line = 0

        env.working_step = 4

    # select recook item confirm
    def on_click311_2(self, name):
        for item in self.text_lists:
            if name == item[0]:
                t = "\n\n".join(item[1])
                self._text = t
                break
        self.text_name = name
        self.recook = True

        env.working_step = 2

    def on_click4_5(self):
        env.working_step = 5
    
    def on_click5_4(self):
        env.working_step = 4
# end of class App


# start the program
env = Env()
env.show.run()
