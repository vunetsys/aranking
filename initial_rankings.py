from database import Database
import pandas as pd

filename = "world-universities.csv"
# included_cols = [1]

query = "select * from affiliations where affiliation like '%University%' OR affiliation like '%Universidad%' or " \
        "affiliation like '%Université%' or affiliation like'%College%' order by country, affiliation asc select * " \
        "from affiliations order by country, affiliation asc"

db = Database()
df = pd.read_csv(filename)

universities = df.iloc[:, [1]].values
affiliations = db.get_affiliations()

found_uni = []

for university in universities:
    uni = university[0]
    print(uni)
    db.c.execute("SELECT * FROM affiliations WHERE affiliation=%s", (uni,))
    result = db.c.fetchall()

    if result:
        found_uni.append(result)



#
# with open(filename, 'r') as reader:
#     for row in reader:
#         print(row[])
        # content = list(row[i] for i in included_cols)
        # print(content)
