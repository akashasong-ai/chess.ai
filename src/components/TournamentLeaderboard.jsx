import PropTypes from 'prop-types';

const TournamentLeaderboard = ({ leaderboard }) => {
  return (
    <div className="tournament-leaderboard">
      <table>
        <thead>
          <tr>
            <th>RANK</th>
            <th>AI MODEL</th>
            <th>WINS</th>
            <th>DRAWS</th>
            <th>LOSSES</th>
            <th>POINTS</th>
          </tr>
        </thead>
        <tbody>
          {leaderboard.map((entry, index) => (
            <tr key={entry.id || index}>
              <td>{index + 1}</td>
              <td>{entry.name}</td>
              <td>{entry.wins}</td>
              <td>{entry.draws}</td>
              <td>{entry.losses}</td>
              <td>{entry.wins * 2 + entry.draws}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

TournamentLeaderboard.propTypes = {
    leaderboard: PropTypes.arrayOf(
        PropTypes.shape({
            id: PropTypes.string.isRequired,
            name: PropTypes.string.isRequired,
            wins: PropTypes.number.isRequired,
            draws: PropTypes.number.isRequired,
            losses: PropTypes.number.isRequired
        })
    ).isRequired
};

export default TournamentLeaderboard;      