from database import Database
import numpy as np
from sklearn import preprocessing
from general import similar
import psycopg2 as p

db = Database()
universities = db.get_universities()
db.c.execute("SELECT name, id from ranking_lists")
ranking_names = db.c.fetchall()

university_list = []
score_list = []

# Reads initial ranking from the files, calculates scores and tries to add everything to the database.

def add_initial_universities():
    for uni in universities:
        id = uni[0]
        name = uni[1]
        country = uni[2]
        try:
            db.c.execute("INSERT INTO ranked_affiliations (id, affiliation, location) VALUES (%s, %s, %s)",
                         (id, name, country))
            db.conn.commit()
        except p.IntegrityError:
            db.conn.rollback()
            db.c.execute("SELECT id from ranked_affiliations where affiliation=%s", (name,))
            new_id = db.c.fetchall()
            db.c.execute("UPDATE authors SET affiliation_id=%s WHERE affiliation_id=%s", (new_id[0][0], id))
            db.c.execute("DELETE FROM affiliations where id=%s", (id,))
            print("UPDATED ID FOR: " + name)


def give_initial_ranking():
    db.c.execute("SELECT * FROM ranking_lists")
    ranking_information = db.c.fetchall()

    for university in ranking_information:
        university_name = university[1]
        qs_rank = university[2]
        the_rank = university[3]
        shanghai_rank = university[4]

        qs_rank = (qs_rank, 0)[qs_rank is None]
        the_rank = (the_rank, 0)[the_rank is None]
        shanghai_rank = (shanghai_rank, 0)[shanghai_rank is None]

        score = calculate_ranking_score(str(qs_rank), str(the_rank), str(shanghai_rank))

        # db.c.execute("UPDATE ranking_lists SET raw_score=%s WHERE name=%s", (score, university_name))
        # db.conn.commit()

        university_list.append(university_name)
        score_list.append(score)

    score_array = np.asarray(score_list)
    scoring = 1 - (preprocessing.minmax_scale(score_array[:, np.newaxis], axis=0).ravel())
    add_to_database(scoring)
    find_match()


def calculate_ranking_score(qs, the, shanghai):
    # There is a different "-" used in the ranking, replace first.
    if "–" in the:
        the = the.replace("–", "-")

    if "-" in qs:
        qs = calculate_average(qs)
    if "-" in the:
        the = calculate_average(the)
    if "-" in shanghai:
        shanghai = calculate_average(shanghai)

    num_rankings = 3

    if int(qs) == 0:
        num_rankings -= 1
    if int(the) == 0:
        num_rankings -= 1
    if int(shanghai) == 0:
        num_rankings -= 1

    return (int(qs) + int(the) + int(shanghai)) / num_rankings


def calculate_average(ranking):
    first_score = "".join(ranking.split("-")[:1])
    second_score = "".join(ranking.split("-")[1:])
    return (int(first_score) + int(second_score)) / 2


def add_to_database(scoring):
    for university, score in zip(university_list, scoring):

        db.c.execute("UPDATE ranking_lists SET normalized_score=%s WHERE name=%s", (score, university))
        db.conn.commit()


def find_match():
    db.c.execute("SELECT name, normalized_score FROM ranking_lists ORDER BY normalized_score DESC")
    score_list = db.c.fetchall()
    found = 0
    has_match = 0

    for entry in score_list:
        has_match = 0
        university = entry[0]
        score = entry[1]
        for uni in universities:
            found_universities = []
            if similar(uni[1], university) > 0.95:
                print(university)
                print("Found: " + str(uni))
                found += 1
                # db.c.execute("UPDATE ranked_affiliations SET ranking=%s WHERE affiliation=%s", (score, university))
                # db.conn.commit()
                has_match = 1
                break

                # elif 0.85 <= similar(uni[1], university) < 1:
                #     user_decision = input("Are " + uni[1] + " and " + university + " the same?")
                # if user_decision == "1":
                #     db.c.execute("UPDATE ranked_affiliations SET ranking=%s WHERE affiliation=%s",
                #                  (score, university))
                #     db.conn.commit()
                #     print("Added " + university + "!")
                #     break
                # else:
                #     print("Continuing to next.")
                #     with open("ranked_universities.txt", 'a') as f:
                #         f.write(uni[1] + " " + str(score) + "\n")
                #     f.close()

        if has_match == 0:
            with open("ranked_universities.txt", 'a') as f:
                f.write(university + " " + str(score) + "\n")
            f.close()

        print(found)

