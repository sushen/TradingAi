class MessageText:

    def first_message(self):
        text =  "This is my first approach to use machin learning for predicting cripto price." \
                " https://youtu.be/Al4g8whYsNw I have a newly created facebook group called" \
                " https://www.facebook.com/groups/talibai I encourage you to join the group."

        # print(text)
        return text

    def secound_message(self):
        text = "Ta-Lib Lighbary is difficult to setup sometime people what to clean data at the same time," \
               "build real application and Build Model, The way I make the setup you can " \
               "do it all from this environment. https://youtu.be/rTIVAECJAnU"
        return text

    def third_message(self):
        text = "How you grab the dataset from internet. https://youtu.be/Plkx91LDasg Its easy to get the data but its always take time."
        return text

    def forth_message(self):
        text = "How to clean the data so you can fid it to the model : " \
               "https://youtu.be/Av-HYvwkFJg"
        return text

    def fifth_message(self):
        text = "Make the visualization so you can understand what you are doing " \
               "https://youtu.be/cvQnoxnNtfU"
        return text

    def sixth_message(self):
        text = "How you can add new Feature to your Model " \
               "https://youtu.be/42sAOeAPajg"
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
        elif input == 5:
            return self.fifth_message()
        elif input == 6:
            return self.sixth_message()


# m = MessageText()
# print(m.ai_text(2))
