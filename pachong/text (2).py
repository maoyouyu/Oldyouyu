from datetime import datetime, timedelta
now = datetime.now()
print(now)
print(type(now))

dt = datetime(1025, 4, 19, 20)
print(dt)


do = datetime(2015, 4, 12, 20)
do.timestamp()

t = 1429417200.0
print(datetime.fromtimestamp(t))
print(datetime.utcfromtimestamp(t))

print(now.strftime('%a, %b %d %H:%M'))

now + timedelta(hours=10)
