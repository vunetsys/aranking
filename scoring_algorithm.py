from database import Database
import math

db = Database()
rank_names = {
    "Artificial Intelligence": "rank_ai",
    "Computational Linguistics": "rank_cl",
    "Computer Graphics": "rank_cg",
    "Computer Hardware Design": "rank_chd",
    "Computer Networks & Wireless Communication": "rank_cnwc",
    "Computer Security & Cryptography": "rank_csc",
    "Computer Vision & Pattern Recognition": "rank_cvpr",
    "Computing Systems": "rank_cs",
    "Data Mining & Analysis": "rank_dma",
    "Databases & Information Systems": "rank_dis",
    "Human Computer Interaction": "rank_hci",
    "Multimedia": "rank_mm",
    "Robotics": "rank_rb",
    "Theoretical Computer Science": "rank_tcs",
}


def conference_scoring(category):
    # Author scores propagaten via goeie conference ranking
    # Zorgen dat alle conferences vanuit de goeie ranking hun shit doorsturen
    print(category)
    cat = rank_names[category]
    print(cat)
    query = "SELECT id, " + str(cat) + " from ranked_affiliations where " + str(cat) + " is not null"
    db.c.execute(query)

    # db.c.execute("SELECT id, ranking FROM ranked_affiliations WHERE ranking IS NOT NULL")
    ranked_unis = db.c.fetchall()
    for uni in ranked_unis:
        id = uni[0]
        ranking = uni[1]
        print(ranking)
        db.c.execute("UPDATE authors set aff_ranking=%s WHERE affiliation_id=%s", (ranking, id))
        db.conn.commit()

    db.c.execute("SELECT id FROM papers WHERE conference_id IN "
                 "(SELECT id FROM conferences WHERE venue_id IN"
                 "(SELECT id FROM venues WHERE category=%s)) ORDER BY id ASC", (category,))
    papers = db.c.fetchall()
    for paper in papers:
        pid = paper[0]
        db.c.execute("SELECT sum(aff_ranking), count(user_id) FROM authors WHERE user_id IN"
                     "(SELECT author_id FROM authors_papers WHERE paper_id=%s) AND aff_ranking IS NOT NULL",
                     (pid,))
        author_rank = db.c.fetchall()[0]
        score = author_rank[0]
        num_authors = author_rank[1]
        print(pid)
        if score is not None:
            # print(num_authors)
            # print(score)
            rank = score / num_authors
            print(rank)
            db.c.execute("UPDATE papers set ranking=%s WHERE id=%s", (rank, pid))
            db.conn.commit()

    db.c.execute("SELECT id FROM conferences WHERE venue_id IN"
                 "(SELECT id FROM venues WHERE category=%s)", (category,))
    conference_ids = db.c.fetchall()
    normalized_score = 0

    for id in conference_ids:
        db.c.execute(
            "SELECT SUM(ranking), count(ranking) FROM papers WHERE conference_id=%s AND ranking IS NOT NULL",
            (id,))
        paper_values = db.c.fetchall()[0]
        if paper_values[0] is not None:
            score = paper_values[0]
            amount = paper_values[1]
            rank = score / amount
            normalized_score += (score * score)
            db.c.execute("UPDATE conferences SET ranking=%s WHERE id=%s", (rank, id))
            db.conn.commit()
            print(str(id) + " " + str(rank))

    normalized_score = math.sqrt(normalized_score)
    db.c.execute("SELECT id, ranking from conferences order by id ASC")
    rankings = db.c.fetchall()

    for ranking in rankings:
        id = ranking[0]
        score = ranking[1]
        if score is not None:
            final_ranking = score / normalized_score
            db.c.execute("UPDATE conferences SET ranking=%s WHERE id=%s", (final_ranking, id))
            db.conn.commit()

    db.c.execute("SELECT id from venues WHERE category=%s order by id asc", (category,))
    venues = db.c.fetchall()
    normalized_score = 0
    for venue in venues:
        venue_id = venue[0]
        db.c.execute(
            "SELECT sum(ranking), count(ranking) FROM conferences WHERE venue_id=%s and ranking IS NOT NULL",
            (venue_id,))
        venue_rank = db.c.fetchall()[0]
        agg_score = venue_rank[0]
        if agg_score is not None:
            num_conferences = venue_rank[1]
            rank = agg_score / num_conferences
            normalized_score += (agg_score * agg_score)
            db.c.execute("UPDATE venues SET ranking=%s WHERE id=%s", (rank, venue_id))
            db.conn.commit()
            print(str(venue_id) + " " + str(rank))
    normalized_score = math.sqrt(normalized_score)
    db.c.execute("SELECT id, ranking from venues WHERE category=%s order by id asc", (category,))
    rankings = db.c.fetchall()

    for ranking in rankings:
        id = ranking[0]
        score = ranking[1]
        if score is not None:
            final_ranking = score / normalized_score
            print(final_ranking)
            db.c.execute("UPDATE venues SET ranking=%s WHERE id=%s", (final_ranking, id))
            db.conn.commit()

    affiliation_scoring(category)

    # for cat in categories:
    #     category = cat[0]
    #     print(category)


def affiliation_scoring(category):
    db.c.execute("SELECT id from ranked_affiliations ORDER BY id ASC")
    affiliation_ids = db.c.fetchall()
    ranking_column = rank_names[category]
    print(ranking_column)

    normalized_score = 0
    for id in affiliation_ids:
        db.c.execute(
            "SELECT SUM(ranking), count(ranking) FROM venues WHERE category=%s AND id IN "
            "(SELECT venue_id from conferences WHERE id IN"
            "(SELECT conference_id FROM papers WHERE id IN "
            "(SELECT paper_id FROM authors_papers WHERE author_id IN "
            "(SELECT user_id FROM authors WHERE affiliation_id=%s)))) "
            "AND ranking is NOT NULL", (category, id[0],))
        found = db.c.fetchall()
        agg_score = found[0][0]
        if agg_score is not None:
            print(agg_score)
            normalized_score += (agg_score * agg_score)
            query = "UPDATE ranked_affiliations SET " + str(ranking_column) + "=%s WHERE id=%s"
            db.c.execute(query, (agg_score, id))
            db.conn.commit()

    normalized_score = math.sqrt(normalized_score)
    query = "SELECT id, " + str(ranking_column) + " from ranked_affiliations order by id ASC"
    db.c.execute(query)
    rankings = db.c.fetchall()

    for ranking in rankings:
        id = ranking[0]
        score = ranking[1]
        if score is not None:
            final_ranking = score / normalized_score
            query = "UPDATE ranked_affiliations SET " + str(ranking_column) + "=%s WHERE id=%s"
            db.c.execute(query, (final_ranking, id))
            print(str(id) + " " + str(final_ranking))
            db.conn.commit()


# conference_scoring()
# affiliation_scoring("Artificial Intelligence")
# conference_scoring()
for value in rank_names:
    conference_scoring(value)
