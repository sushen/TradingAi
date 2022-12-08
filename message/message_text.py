class MessageText:

    def first_message(self):
        text =  "Hi, " \
          "Sushen Biswas teaching programming for more than 4 years." \
          " In our understanding basic programming come from basic math." \
          "Actually its come from kindergarten math. We all know x , y math." \
          "In Bangla We called 'চলক' , In programming we called it variable." \
          "You see 6 class math. We are going to learn like that. to know more" \
          "about Sushen Biswas I give yoy my github profile. Its give you a perception about " \
          "Sushen Biswas creditability.'https://github.com/sushen'. If you think we can help you to learn" \
          "We will be glad to spend time with you."
        # print(text)
        return text

    def secound_message(self):
        text = "For any king of question 'LEARN PYTHON TOGETHER' is here to help you. " \
               "https://www.facebook.com/lpythont "
        return text

    def third_message(self):
        text = "Why 'Compact Learn' help us to learn things quickly and easily. https://wp.me/pb38Tn-3zs this 2 " \
               "minutes reading change your perception why we cant learn easily "
        return text

    def forth_message(self):
        text = "Math is equal important like programming language' https://github.com/sushen/mathandmoremath this " \
               "github repository help you to learn math and programming both. "
        return text

    def fifth_message(self):
        text = "This group help you to connect other python learner. https://www.facebook.com/groups/lptgp don't feel " \
               "same to ask anything publicly "
        return text

    def ai_text(self, input=None):
        if input == 1:
            return self.first_message()
        elif input == 2:
            return self.secound_message()
        elif input == 3:
            return self.third_message()
        elif input == 4:
            return self.forth_message()


# m = MessageText()
# print(m.ai_text(2))
