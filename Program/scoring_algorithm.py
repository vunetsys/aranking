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
num_of_cycles = 1


def conference_scoring():
    ranked_unis = db.get_ranked_unis()
    for uni in ranked_unis:
        id = uni[0]
        ranking = uni[1]
        print(ranking)
        db.c.execute("UPDATE authors set aff_ranking=%s WHERE affiliation_id=%s", (ranking, id))
        db.conn.commit()

    papers = db.get_papers()
    for paper in papers:
        pid = paper[0]
        print(pid)

        author_rank = db.get_author_from_paper(pid)
        score = author_rank[0]
        num_authors = author_rank[1]

        if score is not None:
            rank = score / num_authors
            print(rank)
            db.c.execute("UPDATE papers set ranking=%s WHERE id=%s", (rank, pid))
            db.conn.commit()

    conference_ids = db.get_conferences()
    normalized_score = 0

    for id in conference_ids:
        conf_id = id[0]
        paper_values = db.get_confpaper_score(conf_id)

        if paper_values[0] is not None:
            score = paper_values[0]
            amount = paper_values[1]
            rank = score / amount
            normalized_score += (rank * rank)
            db.c.execute("UPDATE conferences SET ranking=%s WHERE id=%s", (rank, id))
            db.conn.commit()
            print(str(id) + " " + str(rank))

    normalized_score = math.sqrt(normalized_score)
    rankings = db.get_conferences()

    for ranking in rankings:
        id = ranking[0]
        score = ranking[1]
        if score is not None:
            final_ranking = score / normalized_score
            db.c.execute("UPDATE conferences SET ranking=%s WHERE id=%s", (final_ranking, id))
            db.conn.commit()

    venues = db.get_venues_ranking()
    normalized_score = 0
    for venue in venues:
        venue_id = venue[0]
        venue_rank = db.get_venue_score(venue_id)
        agg_score = venue_rank[0]
        if agg_score is not None:
            num_conferences = venue_rank[1]
            rank = agg_score / num_conferences
            normalized_score += (rank * rank)
            db.c.execute("UPDATE venues SET ranking=%s WHERE id=%s", (rank, venue_id))
            db.conn.commit()
            print(str(venue_id) + " " + str(rank))

    normalized_score = math.sqrt(normalized_score)
    rankings = db.get_venues_ranking()

    for ranking in rankings:
        id = ranking[0]
        score = ranking[1]
        if score is not None:
            final_ranking = score / normalized_score
            print(final_ranking)
            db.c.execute("UPDATE venues SET ranking=%s WHERE id=%s", (final_ranking, id))
            db.conn.commit()


def affiliation_scoring():
    affiliation_ids = db.get_affiliation_ids()
    db.c.execute("UPDATE ranked_affiliations SET ranking=NULL")
    db.conn.commit()

    normalized_score = 0
    for id in affiliation_ids:
        found = db.get_affiliation_score(id[0])
        agg_score = found[0][0]
        if agg_score is not None:
            print("Score for affiliation with id: " + str(id[0]) + ": " + str(agg_score))
            normalized_score += (agg_score * agg_score)
            db.c.execute("UPDATE ranked_affiliations SET ranking=%s WHERE id=%s", (agg_score, id))
            db.conn.commit()

    normalized_score = math.sqrt(normalized_score)
    rankings = db.get_affiliation_ids()

    for ranking in rankings:
        id = ranking[0]
        score = ranking[1]
        if score is not None:
            final_ranking = score / normalized_score
            db.c.execute("UPDATE ranked_affiliations SET ranking=%s WHERE id=%s", (final_ranking, id))
            print(str(id) + " " + str(final_ranking))
            db.conn.commit()


for i in range(num_of_cycles):
    conference_scoring()
    affiliation_scoring()
