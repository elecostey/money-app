import sqlite3
from datetime import datetime
import calendar
import datetime as dt


def CurrentDatePlusOneMonth(currentMonth):
    currentYear = str(datetime.now().year)
    currentMonth = str(currentMonth)
    if int(currentMonth) < 10 :
        currentMonth = "0" + currentMonth
    currentDateString = currentYear+'-'+currentMonth+'-01'
    currentDateTime = dt.datetime.strptime(currentDateString, "%Y-%m-%d")
    currentDateInteger = dt.date(currentDateTime.year,currentDateTime.month,currentDateTime.day)
    month = currentDateInteger.month
    year = int(currentDateInteger.year + month / 12)
    month = month % 12 + 1
    day = 01
    newDatetime = dt.datetime(year, month, day)
    newDateString = newDatetime.strftime("%Y-%m-%d")
    return newDateString

def getExpensesTotal(currentMonth):
    conn = sqlite3.connect('squirrel.db')
    conn.text_factory = str
    c = conn.cursor()
    c.execute("""SELECT ammount
                 FROM transactions
                 WHERE transactiontypeid = 2
                 AND transactionduedate <= '%s'
                 ORDER by transactiondate DESC"""% CurrentDatePlusOneMonth(currentMonth))
    expensesList = list(c)
    newExpensesList = []

    for i in expensesList:
        newExpensesList.append(i[0])
    ExpensesTotal = (sum(float(i) for i in newExpensesList))
    conn.commit()
    conn.close()
    return ExpensesTotal

def getIncomeTotal(currentMonth):
    conn = sqlite3.connect('squirrel.db')
    conn.text_factory = str
    c = conn.cursor()
    c.execute("""SELECT ammount
                 FROM transactions
                 WHERE transactiontypeid = 1
                 AND transactionduedate <= '%s'
                 ORDER by transactiondate DESC"""% CurrentDatePlusOneMonth(currentMonth))
    incomeList = list(c)
    newIncomeList = []
    for i in incomeList:
        newIncomeList.append(i[0])
    incomeTotal = (sum(float(i) for i in newIncomeList))
    conn.commit()
    conn.close()
    return incomeTotal

def getAllTransactions(currentMonth):
    year = '%Y'
    month = '%m'
    currentYear = str(datetime.now().year)
    currentMonth = str(currentMonth)
    if int(currentMonth) < 10 :
      currentMonth = "0" + currentMonth

    conn = sqlite3.connect('squirrel.db')
    conn.text_factory = str
    c = conn.cursor()
    c.execute("""SELECT transactions.transactiondate, transactions.ammount, transactions.userid, accounts.accountname, transactiontype.transactiontypename, expensetype.expensetypename
                 FROM transactions
                 INNER JOIN accounts
                 ON transactions.accountid=accounts.accountid
                 INNER JOIN transactiontype
                 ON transactions.transactiontypeid=transactiontype.transactiontypeid
                 INNER JOIN expensetype
                 ON transactions.expensetypeid=expensetype.expensetypeid
                 WHERE strftime('%s',transactionduedate) = '%s'
                 AND strftime('%s',transactionduedate) = '%s'
                 ORDER by transactiondate DESC"""% (month, currentMonth, year, currentYear))
    transactionList = list(c)
    print transactionList
    conn.commit()
    conn.close()
    return transactionList

def getTransactionId(transactionType):
    conn = sqlite3.connect('squirrel.db')
    c = conn.cursor()
    transactionTypeobject = c.execute("SELECT transactiontypeid FROM transactiontype WHERE transactiontypename = '%s'" % transactionType).fetchone()[0]
    conn.commit()
    conn.close()
    return transactionTypeobject

def getAccountId(card):
    conn = sqlite3.connect('squirrel.db')
    c = conn.cursor()
    accountobject = c.execute("SELECT accountid FROM accounts WHERE accountname = '%s'" % card).fetchone()[0]
    conn.commit()
    conn.close()
    return accountobject

def addExpenseToDatabase(time, amount, accountId, transactionType, dueDate):
    conn = sqlite3.connect('squirrel.db')
    c = conn.cursor()
    c.execute("INSERT INTO transactions (transactiondate, ammount, userid, accountid, transactiontypeid, expensetypeid, transactionduedate) VALUES ('%s','%s', 1, '%s', '%s', 1, '%s')"% (time, amount, accountId, transactionType, dueDate))
    conn.commit()
    conn.close()
