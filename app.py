from flask import Flask, render_template, request, url_for, redirect
from babel.numbers import format_currency
import sqlite3
import datetime as dt
import calendar
from databaseutil import *

app = Flask(__name__)

@app.context_processor
def utility_processor():
    def formatPrice(price):
        return format_currency(price, 'kn', locale='de_DE')
    return dict(formatPrice=formatPrice)

@app.context_processor
def utility_processor():
    def convertDateTimeToReadable(dateToConvert):
        dateTime = dt.datetime.strptime(dateToConvert, "%Y-%m-%d")
        return dateTime.strftime('%A, %d %B %Y')
    return dict(convertDateTimeToReadable=convertDateTimeToReadable)


def findDueDateManualTransaction(dateInteger, card):
  if card == 'Maestro':
    month = dateInteger.month - 1
  else:
    if dateInteger.day < 15:
      month = dateInteger.month
    else:
      month = dateInteger.month + 1
  year = int(dateInteger.year + month / 12)
  month = month % 12 + 1
  day = min(dateInteger.day, calendar.monthrange(year, month)[1])
  newDatetime = dt.datetime(year, month, day)
  dueDate = newDatetime.strftime("%Y-%m-%d")
  return dueDate

def findDueDateAutomatedTransaction(dateInteger, months, card):
  dueDateList = []
  numberToIncrease = 0
  while numberToIncrease < int(months):
    if card == 'Maestro':
      month = dateInteger.month - 1 + numberToIncrease
    else:
      if dateInteger.day < 15:
        month = dateInteger.month + numberToIncrease
      else:
        month = dateInteger.month + 1 + numberToIncrease
    year = int(dateInteger.year + month / 12)
    month = month % 12 + 1
    day = min(dateInteger.day, calendar.monthrange(year, month)[1])
    newDatetime = dt.datetime(year, month, day)
    newDate = newDatetime.strftime("%Y-%m-%d")
    dueDateList.append(newDate)
    numberToIncrease += 1
  return dueDateList



def selected_month_name(selectedMonth):
  for month in myMonthsList:
    if month[1] == int(selectedMonth):
      selectedMonthName = month[0]
  return selectedMonthName

# Current date variable ---------------------------------------------------------
currentMonth = datetime.now().month
# ------------------------------------------------------------------------------
initialBalance = -10000
myMonthsList = [('January', 1), ('February', 2),('March', 3),('April', 4),('May', 5),('June', 6),('July', 7),
                ('August', 8), ('September', 9), ('October', 10), ('November', 11), ('December', 12)]

@app.route('/')
def index():
    balance = initialBalance - getExpensesTotal(currentMonth) + getIncomeTotal(currentMonth)

    currentMonthName = datetime.now().strftime('%B')
    return render_template('addNewExpense.html',
                            transactions = getAllTransactions(currentMonth),
                            currentMonth = currentMonth,
                            balance = balance,
                            selectedMonthName=currentMonthName,
                            months = myMonthsList)

@app.route('/changeMonth', methods=['POST'])
def changeMonth():
    selectedMonth = request.form['months']
    currentMonth = int(selectedMonth)
    balance = initialBalance - getExpensesTotal(currentMonth) + getIncomeTotal(currentMonth)

    print balance
    print type(balance)
    return render_template('addNewExpense.html',
                            transactions = getAllTransactions(currentMonth),
                            currentMonth = currentMonth,
                            selectedMonthName=selected_month_name(selectedMonth),
                            balance = balance,
                            months = myMonthsList)

@app.route('/goToAutomatedPayment')
def goToAutomatedPayment():
    return render_template('addAutomatedPayment.html')

@app.route('/addAutomatedPayment', methods=['POST'])
def addAutomatedPayment():
    paymentDate = request.form['paymentDate']
    paymentDateTime = dt.datetime.strptime(paymentDate, "%Y-%m-%d")
    paymentDateInteger = dt.date(paymentDateTime.year,paymentDateTime.month,paymentDateTime.day)
    paymentRates = request.form['paymentRates']
    paymentAmount = request.form['paymentAmount']
    paymentCards = request.form.get('paymentCards')
    paymentType = request.form.get('paymentType')
    paymentDueDate = findDueDateAutomatedTransaction(paymentDateInteger, paymentRates, paymentCards)
    for i in paymentDueDate:
        addExpenseToDatabase(i, paymentAmount, getAccountId(paymentCards), getTransactionId(paymentType), i)
    return redirect(url_for('index'))


@app.route('/addNewExpense', methods=['POST'])
def addExpense():
    date = request.form['date']
    dateTime = dt.datetime.strptime(date, "%Y-%m-%d")
    dateInteger = dt.date(dateTime.year,dateTime.month,dateTime.day)
    amount = request.form['amount']
    cardType = request.form.get('cards')
    transactionType = request.form.get('transactionType')
    dueDate = findDueDateManualTransaction(dateInteger, cardType)
    addExpenseToDatabase(date, amount, getAccountId(cardType), getTransactionId(transactionType), dueDate)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
