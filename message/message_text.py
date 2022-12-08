class MessageText:

    def first_message(self):
        text =  "This is my first approach to use machin learning for predicting cripto price." \
                " https://youtu.be/Al4g8whYsNw I have a newly created facebook group called" \
                " https://www.facebook.com/groups/talibai I encourage you to join the group."

        # print(text)
        return text

    def secound_message(self):
        text = "Ta-Lib Lighbary is difficult to setup sometime people what to clean data at the same time," \
               "build real application and Build Model, The way I make the setup you can" \
               "do it all from this environment. https://youtu.be/rTIVAECJAnU"
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
