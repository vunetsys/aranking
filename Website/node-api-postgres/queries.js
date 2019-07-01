const Pool = require('pg').Pool
const pool = new Pool({
  user: 'lucas',
  host: 'localhost',
  database: 'rankedcategories',
  port: 5432,
})

const getVenues = (request, response) => {
  pool.query('SELECT name, category, rank_final, ranking FROM venues ORDER BY ranking DESC', (error, results) => {
    if (error) {
      throw error
    }
    response.status(200).json(results.rows)
  })
}

const getAffiliations = (request, response) => {
  pool.query('SELECT affiliation, location, rank_final, ranking, id FROM ranked_affiliations WHERE ranking >= 0.00660021655834795 ORDER BY ranking DESC', (error, results) => {
    if (error) {
      throw error
    }
    response.status(200).json(results.rows)
  })
}

const getPublishedVenues = (request, response) => {
  const id = request.params.id

  pool.query("SELECT name, rank_final, ranking FROM venues WHERE id IN (SELECT venue_id from conferences WHERE id IN (SELECT conference_id FROM papers WHERE id IN (SELECT paper_id FROM authors_papers WHERE author_id IN (SELECT user_id FROM authors WHERE affiliation_id=$1)))) ORDER BY ranking DESC", [id], (error, results) => {
    if (error) {
      throw error
    }
    response.status(200).json(results.rows)
  })
}

// function getPublicatedVenues(affiliation_id) = (request, response) => {

//   s = parse('"SELECT SUM(ranking), count(ranking) FROM venues WHERE id IN (SELECT venue_id from conferences WHERE id IN" \
//             " (SELECT conference_id FROM papers WHERE id IN " \
//             "(SELECT paper_id FROM authors_papers WHERE author_id IN " \
//             "(SELECT user_id FROM authors WHERE affiliation_id=%s))))"', affiliation_id);
//   pool.query(s, (error, results) => {
//     if (error){
//         throw error
//     }
//     response.status(200).json(results.rows)
//     })
// }

module.exports = {
	getVenues,
  getAffiliations,
  getPublishedVenues
}