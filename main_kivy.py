import os
# Kivy needs specific environment variables set sometimes, especially on Windows
# This tries to configure logging and graphics before other Kivy imports
os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2' # Or 'sdl2' or 'glew'
os.environ['KIVY_LOG_LEVEL'] = 'info' # Or 'debug' for more details

import kivy
kivy.require('2.1.0') # Specify Kivy version compatibility (optional but good practice)

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.metrics import dp # For density-independent pixels

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
# Note: For a real app, save/load the model instead of retraining each time
# import joblib # Use joblib or pickle to save/load the trained model

# --- Machine Learning Model Setup (Same as before, but consider saving/loading) ---
data = {
    'text': [
        "Free entry in 2 a wkly comp to win FA Cup final tkts 21st May 2005.",
        "Nah I don't think he goes to usf, he lives around here though",
        "FreeMsg Hey there darling it's been 3 week's now and no word back!",
        "Even my brother is not like to speak with me. They treat me like aids patent.",
        "WINNER!! As a valued network customer you have been selected to receivea £900 prize reward!",
        "I'm gonna be home soon and i don't want to talk about this stuff anymore tonight, k?",
        "Had your mobile 11 months or more? U R entitled to Update to the latest colour mobiles with camera for Free!",
        "Okay lar... Joking wif u oni...",
        "URGENT! You have won a 1 week FREE membership in our £100,000 Prize Jackpot!",
        "Fine if that's the way u feel. That's the way its gota b"
    ],
    'label': ['spam', 'ham', 'spam', 'ham', 'spam', 'ham', 'spam', 'ham', 'spam', 'ham']
}
df = pd.DataFrame(data)
model = make_pipeline(TfidfVectorizer(), MultinomialNB())
model.fit(df['text'], df['label'])
# --- End ML Setup ---

class SpamDetectorLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(15)
        self.spacing = dp(10)

        # Input Label
        self.add_widget(Label(text='Email Text Input:', size_hint_y=None, height=dp(30), halign='left', text_size=(Window.width - dp(30), None)))

        # Text Input Area (inside a ScrollView for longer text)
        scroll_view = ScrollView(size_hint=(1, 1)) # Takes available vertical space
        self.text_input = TextInput(
            multiline=True,
            size_hint=(1, None), # Take full width, height adjusts
            font_size=dp(16)
        )
        self.text_input.bind(minimum_height=self.text_input.setter('height')) # Auto-adjust height
        scroll_view.add_widget(self.text_input)
        self.add_widget(scroll_view) # Add the ScrollView containing the TextInput

        # Check Button
        self.check_button = Button(
            text='Check for Spam',
            size_hint_y=None,
            height=dp(50),
            font_size=dp(18)
        )
        self.check_button.bind(on_press=self.check_spam)
        self.add_widget(self.check_button)

        # Result Label
        self.result_label = Label(
            text='Prediction will appear here',
            size_hint_y=None,
            height=dp(40),
            font_size=dp(16),
            color=(0.5, 0.5, 0.5, 1) # Grey color
        )
        self.add_widget(self.result_label)

    def predict_spam_internal(self, text):
        """Internal prediction logic."""
        if not text.strip():
            return "Enter some text first!", (0.5, 0.5, 0.5, 1) # Text, Color tuple
        try:
            prediction = model.predict([text])
            probability = model.predict_proba([text])
            prob_percent = probability[0, model.classes_.tolist().index(prediction[0])] * 100
            result_text = f"Prediction: {prediction[0].upper()} ({prob_percent:.2f}%)"

            if prediction[0] == 'spam':
                color = (1, 0.2, 0.2, 1) # Reddish
            else:
                color = (0.2, 1, 0.2, 1) # Greenish
            return result_text, color
        except Exception as e:
            return f"Error: {e}", (1, 0.2, 0.2, 1) # Reddish for error

    def check_spam(self, instance):
        """Callback for the button press."""
        email_text = self.text_input.text
        result_text, result_color = self.predict_spam_internal(email_text)
        self.result_label.text = result_text
        self.result_label.color = result_color


class SpamDetectorApp(App):
    def build(self):
        Window.clearcolor = (0.95, 0.95, 0.95, 1) # Set a light background color for the window
        return SpamDetectorLayout()


if __name__ == '__main__':
    SpamDetectorApp().run()