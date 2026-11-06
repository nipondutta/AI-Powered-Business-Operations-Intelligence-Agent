from pathlib import Path
import csv,random
from datetime import date,timedelta
random.seed(42); out=Path("data/sample"); out.mkdir(parents=True,exist_ok=True)
products=[("P001","Wireless Headphones","Electronics",2499,1400),("P002","Smart Watch","Electronics",3999,2300),("P003","Coffee Maker","Home",3299,1900),("P004","Running Shoes","Fashion",2799,1500),("P005","Backpack","Fashion",1499,700),("P006","Desk Lamp","Home",999,400)]
cities=["Kolkata","Mumbai","Delhi","Bengaluru","Pune","Hyderabad"]
customers=[(f"C{i:04}",f"Customer {i}",f"customer{i}@example.com",random.choice(cities),date(2024,1,1)+timedelta(days=random.randint(0,700)),random.choice(["New","Returning","VIP"])) for i in range(1,251)]
def write(name,header,rows):
    with (out/name).open("w",newline="",encoding="utf-8") as f:
        w=csv.writer(f); w.writerow(header); w.writerows(rows)
write("customers.csv",["customer_id","name","email","city","signup_date","segment"],customers)
write("products.csv",["product_id","product_name","category","unit_price","cost_price"],products)
orders=[]
for i in range(1,1801):
    c=random.choice(customers); p=random.choice(products); d=date(2025,1,1)+timedelta(days=random.randint(0,364))
    orders.append((f"O{i:05}",c[0],p[0],d,random.randint(1,4),p[3],random.choice([0,.05,.1,.15]),random.choices(["delivered","shipped","cancelled","refunded"],[78,12,6,4])[0]))
write("orders.csv",["order_id","customer_id","product_id","order_date","quantity","unit_price","discount","status"],orders)
msgs=[("Delivery","negative","My order arrived much later than promised."),("Refund","negative","I requested a refund but have not received the money."),("Product quality","negative","The product stopped working after two days."),("Payment","negative","Payment was deducted but the order was not confirmed."),("Returns","neutral","Please explain how I can return this item."),("Product information","positive","The product description was clear and helpful."),("Delivery","positive","The package arrived earlier than expected.")]
tickets=[]
for i in range(1,401):
    cat,sent,msg=random.choice(msgs); tickets.append((f"T{i:04}",random.choice(customers)[0],date(2025,1,1)+timedelta(days=random.randint(0,364)),cat,random.choice(["low","medium","high"]),sent,random.choice(["open","closed","in_progress"]),msg))
write("tickets.csv",["ticket_id","customer_id","created_at","category","priority","sentiment","status","message"],tickets)
print("Synthetic CSV data generated in data/sample")
