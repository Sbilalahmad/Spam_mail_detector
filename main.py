import tkinter as tk
# Remove messagebox, keep scrolledtext and ttk
from tkinter import scrolledtext, ttk
from tkinter import filedialog # Add filedialog for opening files
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
# Remove train_test_split
# from sklearn.model_selection import train_test_split
import sv_ttk # Import the theme library
import email # Add email library for parsing .eml files
from email import policy # Import policy for modern parsing
import traceback # For error handling

# --- Tooltip Class ---
class Tooltip:
    """
    Creates a tooltip (pop-up hint) for a given widget.
    """
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        widget.bind("<Enter>", self.show_tooltip)
        widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25

        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True) # Remove window decorations
        tw.wm_geometry(f"+{x}+{y}")

        label = tk.Label(tw, text=self.text, justify='left',
                         background="#ffffe0", relief='solid', borderwidth=1, # Light yellow background
                         font=("Segoe UI", "8", "normal"))
        label.pack(ipadx=1)

    def hide_tooltip(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
        self.tooltip_window = None

# --- Machine Learning Model Setup ---

# 1. Sample Data (very small dataset for demonstration)
# In a real application, you'd use a much larger dataset (e.g., from a CSV file)
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
    'label': ['spam', 'ham', 'spam', 'ham', 'spam', 'ham', 'spam', 'ham', 'spam', 'ham'] # ham = not spam
}
df = pd.DataFrame(data)

# 2. Create and Train the Model Pipeline
# Simple pipeline: TF-IDF Vectorizer -> Naive Bayes Classifier
model = make_pipeline(TfidfVectorizer(), MultinomialNB())

# Train the model on the sample data
model.fit(df['text'], df['label'])

def predict_spam(text):
    """Predicts if a given text is spam or ham."""
    if not text.strip():
        return "Enter some text first!"
    try:
        prediction = model.predict([text])
        probability = model.predict_proba([text])
        # Get the probability of the predicted class
        prob_percent = probability[0, model.classes_.tolist().index(prediction[0])] * 100
        return f"Prediction: {prediction[0].upper()} ({prob_percent:.2f}%)"
    except Exception as e:
        return f"Error during prediction: {e}"

# --- Tkinter UI Setup ---

def check_spam():
    """Gets text from input, predicts, and updates the result label."""
    email_text = text_input.get("1.0", tk.END)
    result = predict_spam(email_text)
    # Adjust colors for better visibility with themes
    if "SPAM" in result:
        result_label.config(text=result, foreground="#F44336") # A clearer red
    elif "HAM" in result:
        result_label.config(text=result, foreground="#4CAF50") # A clearer green
    else:
        # Use ttk's theme color for default text if possible, else black
        try:
            default_fg = style.lookup('TLabel', 'foreground')
            result_label.config(text=result, foreground=default_fg)
        except tk.TclError:
             result_label.config(text=result, foreground="grey") # Fallback


def load_and_check_eml():
    """Opens a .eml file, extracts body, puts it in text input, and checks."""
    filepath = filedialog.askopenfilename(
        title="Open Email File",
        filetypes=[("Email files", "*.eml"), ("All files", "*.*")]
    )
    if not filepath:
        return # User cancelled

    try:
        with open(filepath, 'rb') as f: # Read as bytes
            msg = email.message_from_bytes(f.read(), policy=policy.default)

        # Extract subject for context (optional)
        subject = msg.get('subject', '[No Subject]')
        print(f"Loaded email with subject: {subject}") # Log to console

        # Extract body
        body = get_email_body(msg)

        # Clear previous text and insert new body
        text_input.delete("1.0", tk.END)
        text_input.insert("1.0", body)

        # Automatically run the check
        check_spam()

    except Exception as e:
        result_label.config(text=f"Error loading/parsing file: {e}", foreground="orange")
        print("--- Error loading .eml file ---")
        traceback.print_exc()
        print("-------------------------------")


# Main window
root = tk.Tk()
root.title("Spam Detector")
root.geometry("550x400")

# Apply the sv-ttk theme (try 'light' or 'dark')
sv_ttk.set_theme("light") # Or use "dark"

# Apply a ttk style (needed for some ttk widget configurations)
style = ttk.Style(root)
# The theme is primarily set by sv_ttk, but style object can be used for specific tweaks

# --- Define custom styles ---
# Style for the button
style.configure('Colored.TButton',
                font=('Segoe UI', 10, 'bold'),
                background='#2196F3', # Blue background
                foreground='white')   # White text
# Map states (like 'active' - when pressed) to potentially different colors if needed
style.map('Colored.TButton',
          background=[('active', '#1976D2')]) # Darker blue when pressed


# Main frame for better organization and padding
# Use padding consistent with the theme's feel
main_frame = ttk.Frame(root, padding="15 15 15 15") # Increased padding slightly
main_frame.pack(fill=tk.BOTH, expand=True)


# Input Text Area
input_label = ttk.Label(main_frame, text="Email Text Input:")
input_label.pack(pady=(0, 5), anchor="w")

# Frame for scrolled text - sv-ttk might style this automatically
# Keep the frame for structure if needed, or simplify if theme handles borders well
text_frame = ttk.Frame(main_frame) # Removed border/relief, let theme handle it
text_frame.pack(pady=5, padx=0, fill=tk.BOTH, expand=True)

# Use a font size that works well with the theme
# Add background (bg) and foreground (fg) colors directly to ScrolledText
text_input = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, width=60, height=12,
                                       font=("Segoe UI", 10),
                                       bg="#E3F2FD", # Light blue background
                                       fg="#0D47A1") # Dark blue text
text_input.pack(pady=0, padx=0, fill=tk.BOTH, expand=True)
Tooltip(text_input, "Paste email text here, or load from a .eml file using the button below.")


# --- Buttons Frame ---
# Create a frame to hold the buttons side-by-side
buttons_frame = ttk.Frame(main_frame)
buttons_frame.pack(pady=20)

# Load EML Button
load_button = ttk.Button(buttons_frame, text="Load & Check .eml File", command=load_and_check_eml, width=25)
load_button.pack(side=tk.LEFT, padx=5) # Pack side-by-side
Tooltip(load_button, "Click to load an email from a .eml file and check it for spam.")

# Check Button (Manual Input)
# Apply the custom style 'Colored.TButton'
check_button = ttk.Button(buttons_frame, text="Check Pasted Text", command=check_spam, width=20, style='Colored.TButton')
check_button.pack(side=tk.LEFT, padx=5) # Pack side-by-side
Tooltip(check_button, "Click to analyze the text currently pasted in the box above.")


# Result Label
# Use a slightly larger, bold font for the result
result_label = ttk.Label(main_frame, text="Prediction will appear here", font=("Segoe UI", 12, "bold"), wraplength=500, anchor="center", foreground="grey")
result_label.pack(pady=(5, 10), fill=tk.X)


# Start the UI event loop
root.mainloop()