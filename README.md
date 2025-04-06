# Purrfect Care – Your Wellness Companion

**The cutest cat you've ever seen is here to peer pressure you into taking care of yourself while you work!**

Purrfect Care is a desktop wellness application designed to promote healthy work habits by reminding you to take breaks. Inspired by the Wellness track at our hackathon, our playful cat—Patches—motivates you to step away from your screen, drink water, stretch, and simply look up from your work.

## Overview

In today’s demanding work environment, maintaining physical and mental health is crucial. Purrfect Care uses engaging cat animations and interactive notifications to ensure you never miss a break. Whether you're deep in coding or immersed in creative work, Patches is there to help you practice self-care without sacrificing productivity.

## Features

- **Wellness Break Reminders:** Timed notifications prompt you to hydrate, rest your eyes, or stretch.
- **Animated Cat Companion:** Patches provides fun, visual encouragement to step away and care for yourself.
- **Interactive Notifications:** Custom, draggable dialogs appear centered on your screen so you never miss your break.
- **Chat with Patches:** Enjoy uplifting conversations with your AI-powered cat friend to boost your mood and well-being.
- **Built-In To-Do List:** Organize your tasks alongside your wellness breaks within one integrated interface.
- **Adaptive Design:** Our coordinate-based design works across various screen sizes, ensuring a consistent user experience.
- **Portable & Lightweight:** Ideal for hackathons and busy workdays, helping you integrate wellness effortlessly into your routine.

## Inspiration & What It Does

**Inspiration:**  
Purrfect Care was built to merge technology with self-care practices. Our goal is to help you stay motivated, healthy, and productive throughout your workday by blending fun, interactive elements with essential wellness reminders. For additional insights on taking better breaks, see [How to Take Better Breaks at Work, According to Research](https://hbr.org/2023/05/how-to-take-better-breaks-at-work-according-to-research) by Harvard Business Review.

**What It Does:**  
- Acts as a timer that reminds you to take necessary breaks.
- Uses engaging cat animations to encourage you to step away from the screen.
- Integrates chat and task management features so you can maintain both work and wellness seamlessly.

## How We Built It

- **Languages & Frameworks:** Python, PyQt5, and Pygame   
- **Design:** Custom GIFs and images arranged using coordinate-based placement  
- **Challenges:**  
  - Adapting to various laptop screen sizes.
  - Ensuring proper placement of animations and text across different devices.

## Accomplishments & Lessons Learned

- **Accomplishments:**  
  - Successfully integrated notifications, chat, and a to-do list into a single cohesive application.
  - Overcame screen size variability challenges with coordinate-based design adjustments.
- **Lessons Learned:**  
  - The importance of adaptive design in building user-friendly applications.
  - Balancing fun and productivity while maintaining a professional look.

## Getting Started

### Prerequisites

- **Python 3.6+**
- **PyQt5:** For building the user interface.
- **PyAutoGUI:** For screen size detection.
- **Google Generative AI SDK:** For chat functionality (API key required).
- **Additional Dependencies:** Install other required libraries via pip.

### Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/purrfect-care.git
   cd purrfect-care
   ```

2. **Install Dependencies:**

   ```bash
   pip install PyQt5 pyautogui google-generativeai
   ```

3. **Configure Your API Key:**

   Launch the application and navigate to **Settings > Set API Key** to enter your API key, or update the key directly in the source code.

4. **Run the Application:**

   ```bash
   python main.py
   ```

## Usage

When Purrfect Care launches, Patches sits at the bottom of your screen, watching you work. At scheduled intervals, a centered notification dialog prompts you to take a break. You can then:

- **Chat with Patches:** Open the chat window to receive motivational messages and engage in a fun conversation.
- **Manage Your Tasks:** Use the integrated to-do list to organize both your work and wellness tasks.
- **Customize Your Experience:** Right-click on the main window to access additional settings and options.

## Project Structure

```
purrfect-care/
├── assets/                  # Images, GIFs, and fonts used in the application  
│   ├── cat_assets/         # Cat assets provided by [ToffeeCraft](https://toffeecraft.itch.io/)
│   └── fonts/              # Font "dogica" downloaded from DaFont
├── chat_dialog.py           # Chat interface and AI interaction logic
├── main.py                  # Main application file that initializes and runs Purrfect Care
├── notification_dialog.py   # Custom notification dialog for break reminders
├── to_do_list.py            # To-do list widget for task management
└── README.md                # This documentation file
```

## Acknowledgments

- **Wellness Inspiration:** Special thanks to the Hackathon organizers and the wellness community for inspiring this project.
- **Reference:** [How to Take Better Breaks at Work, According to Research](https://hbr.org/2023/05/how-to-take-better-breaks-at-work-according-to-research) – Harvard Business Review.
- **Cat Assets:** Provided by [ToffeeCraft](https://toffeecraft.itch.io/).
- **Font:** "dogica" downloaded from [DaFont](https://www.dafont.com/).
- **Tool Makers:** Gratitude to the developers of PyQt5, Pygame, and Google Generative AI for their robust, open-source tools.
- **LLM support:** ChatGPT & Claude
- **Team Effort:** A big shout-out to our team for their creativity, resilience, and passion in bringing Purrfect Care to life.

---

Enjoy your breaks, stay healthy, and let Patches remind you to care for yourself while you work!
