from database import Database
import math

db = Database()


def conference_scoring():
    db.c.execute("SELECT id, ranking from ranked_affiliations where ranking is not null")
    ranked_unis = db.c.fetchall()
    for uni in ranked_unis:
        id = uni[0]
        ranking = uni[1]
        print(ranking)
        db.c.execute("UPDATE authors set aff_ranking=%s WHERE affiliation_id=%s", (ranking, id))
        db.conn.commit()

    db.c.execute("SELECT id FROM papers ORDER BY id ASC")
    papers = db.c.fetchall()

    for paper in papers:
        id = paper[0]
        print(id)
        db.c.execute("SELECT SUM(aff_ranking), count(user_id) FROM authors WHERE user_id IN  "
                     "(SELECT author_id from authors_papers where paper_id=%s) AND aff_ranking IS NOT NULL", (id,))
        author_rank = db.c.fetchall()[0]
        score = author_rank[0]
        num_authors = author_rank[1]
        if score is not None:
            rank = score / num_authors
            print(rank)
            db.c.execute("UPDATE papers set ranking=%s WHERE id=%s", (rank, id))
            db.conn.commit()

    db.c.execute("SELECT DISTINCT conference_id FROM papers ORDER BY conference_id ASC")
    conference_ids = db.c.fetchall()
    normalized_score = 0
    for id in conference_ids:
        db.c.execute("SELECT SUM(ranking), count(ranking) FROM papers WHERE conference_id=%s AND ranking IS NOT NULL",
                     (id,))
        paper_values = db.c.fetchall()[0]
        if paper_values[0] is not None:
            score = paper_values[0]
            amount = paper_values[1]
            rank = score
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

    db.c.execute("SELECT DISTINCT id from venues order by id asc")
    venues = db.c.fetchall()
    normalized_score = 0
    for venue in venues:
        venue_id = venue[0]
        db.c.execute("SELECT sum(ranking), count(ranking) FROM conferences WHERE venue_id=%s and ranking IS NOT NULL",
                     (venue_id,))
        venue_rank = db.c.fetchall()[0]
        agg_score = venue_rank[0]
        if agg_score is not None:
            num_conferences = venue_rank[1]
            rank = agg_score
            normalized_score += (agg_score*agg_score)
            db.c.execute("UPDATE venues SET ranking=%s WHERE id=%s", (rank, venue_id))
            db.conn.commit()
            # print(str(venue_id) + " " + str(rank))
    normalized_score = math.sqrt(normalized_score)
    db.c.execute("SELECT id, ranking from venues order by id ASC")
    rankings = db.c.fetchall()

    for ranking in rankings:
        id = ranking[0]
        score = ranking[1]
        if score is not None:
            final_ranking = score / normalized_score
            db.c.execute("UPDATE venues SET ranking=%s WHERE id=%s", (final_ranking, id))
            db.conn.commit()


def affiliation_scoring():
    db.c.execute("SELECT id from ranked_affiliations ORDER BY id ASC")
    affiliation_ids = db.c.fetchall()

    normalized_score = 0
    for id in affiliation_ids:
        db.c.execute(
            "SELECT SUM(ranking), count(ranking) FROM venues WHERE id IN (SELECT venue_id from conferences WHERE id IN"
            " (SELECT conference_id FROM papers WHERE id IN "
            "(SELECT paper_id FROM authors_papers WHERE author_id IN "
            "(SELECT user_id FROM authors WHERE affiliation_id=%s)))) "
            "AND ranking is NOT NULL", (id[0],))
        found = db.c.fetchall()
        agg_score = found[0][0]
        if agg_score is not None:
            print(agg_score)
            normalized_score += (agg_score * agg_score)
            db.c.execute("UPDATE ranked_affiliations SET ranking=%s WHERE id=%s", (agg_score, id))
            db.conn.commit()

    normalized_score = math.sqrt(normalized_score)
    db.c.execute("SELECT id, ranking from ranked_affiliations order by id ASC")
    rankings = db.c.fetchall()

    for ranking in rankings:
        id = ranking[0]
        score = ranking[1]
        if score is not None:
            final_ranking = score / normalized_score
            db.c.execute("UPDATE ranked_affiliations SET ranking=%s WHERE id=%s", (final_ranking, id))
            print(str(id) + " " + str(final_ranking))
            db.conn.commit()


conference_scoring()
affiliation_scoring()
