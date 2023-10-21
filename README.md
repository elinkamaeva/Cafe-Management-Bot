# Cafe Management Telegram Bot
This README provides an overview of the Cafe Management Telegram Bot, a comprehensive solution designed to streamline the operations of a cafe or restaurant through Telegram. With features ranging from handling orders to generating sales reports, this bot is an essential tool for modern, efficient cafe management.

## Features
- __Order Management:__ Allows users to create new orders, specifying details about menu items and quantities. The bot integrates a dynamic menu with prices, ensuring a seamless ordering process.
- __Menu Modification__: Users with privileges can alter the menu by adding new items or changing the prices of existing ones, allowing for real-time updates to the cafe's offerings.
- __Order Summation__: Calculates the total for orders, providing users with immediate cost assessments and facilitating quick transactions.
- __Access Control__: Features a user authorization system, where access is granted or denied based on user credentials. This ensures that only authorized personnel can make administrative changes.
- __Daily Sales Reports__: Generates detailed daily sales statistics, including total revenue and item-wise sales, essential for tracking business performance.
- __Monthly and Custom Periodic Reports__: Beyond daily stats, the bot can compile sales data for any specified period, providing insights into monthly performance or during a custom-defined range.
- __Interactive Calendar for Reporting__: Integrates an interactive calendar, simplifying the process of selecting specific dates or periods for sales reporting.

## Getting Started
These instructions will help you deploy your copy of the bot on your server.

### Prerequisites
- Python 3.6 or higher
- Flask micro web framework
- SQLite for database management
- Pytz for timezone calculations

### Installation
1. Clone the repository to your local machine.
2. Install the required dependencies by running ```pip install -r requirements.txt```.
3. Before starting the bot, you need to generate the __cafe.db__ file by running the __db.py__ script. This script will create a SQLite database with the necessary structure for the bot's operations.
   ```bash
   python db.py
   ```
4. Set up your Telegram bot by communicating with the BotFather and getting your token.
5. Update the __conf.py__ file with your specific token and other relevant configurations.
6. Deploy your Flask application.
7. Set the webhook by pointing it to the URL provided by your deployed Flask application.

### Usage
Start the bot by sending the __/start__ command. The bot will introduce its capabilities and provide a list of available commands depending on the user's authorization level.  
  
For managing orders or modifying the menu, follow the interactive dialogues provided by the bot, ensuring to input valid information as prompted.  
  
For generating sales reports, use the respective commands and select the desired dates if necessary, using the integrated calendar for ease of use.

## License
This project is licensed under the MIT License - see the __LICENSE.md__ file for details.
