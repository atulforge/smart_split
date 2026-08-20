import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="MY_SQL_PASSWORD",
    database="smart_split"
)
s = db.cursor()
group_id=1
s.execute('SELECT* FROM expenses')
# print(cursor.column_names)
expenses = s.fetchall()
total_expense = 0
for expense in expenses :
    total_expense+=expense[3]
print('total expense',total_expense)
s.execute('SELECT * FROM users')
users= s.fetchall()
for user in users:
    print(user)
s.execute("SELECT* FROM group_members")
group_members = s.fetchall()
for group_member in group_members:
    print (group_member)
expense_split = total_expense/len(group_members)
print(expense_split)
paid_by_users = {}

# Add every group member
for member in group_members:
    user_id = member[2]
    paid_by_users[user_id] = 0

# Add the expenses each person actually paid
for expense in expenses:
    user_id = expense[2]
    amount = expense[3]

    paid_by_users[user_id] += amount
balances = {}

for user_id, amount_paid in paid_by_users.items():
    balances[user_id] = amount_paid - expense_split

print("Balances:")

for user_id, balance in balances.items():
    print(user_id, balance)
receivers = {}
payers = {}

for user_id, balance in balances.items():

    if balance > 0:
        receivers[user_id] = balance

    elif balance < 0:
        payers[user_id] = -balance


settlements = []

for payer_id, amount_owed in payers.items():

    for receiver_id, amount_to_receive in receivers.items():

        amount = min(amount_owed, amount_to_receive)

        settlements.append(
            (payer_id, receiver_id, amount)
        )

        amount_owed -= amount
        receivers[receiver_id] -= amount

        if amount_owed == 0:
            break

print("Settlements:")

for settlement in settlements:
    print(
        "User", settlement[0],
        "pays User", settlement[1],
        "₹", settlement[2]
    )
s.execute(
    "DELETE FROM settlements WHERE group_id = %s",
    (group_id,)
)
for payer_id, receiver_id, amount in settlements:

    query = """
           INSERT INTO settlements
           (group_id , from_user, to_user, amount, status_, settlement_date)
           VALUES (%s,%s, %s, %s, %s, NOW())
           """
       
    values = (
             group_id,
             payer_id,
             receiver_id,
             amount,
             "pending"
    )

    s.execute(query, values)

db.commit()

print("Settlements saved to database!")



print("Receivers:", receivers)
print("Payers:", payers)
# Select a group
group_id = 1

s.execute(
    "SELECT * FROM group_members WHERE group_id = %s",
    (group_id,)
)

group_members = s.fetchall()

s.execute(
    "SELECT * FROM expenses WHERE group_id = %s",
    (group_id,)
)

expenses = s.fetchall()

print("Group ID:", group_id)
print("Members:", group_members)
print("Expenses:", expenses)
print("Database connected successfully!")