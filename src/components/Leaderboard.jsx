const Leaderboard = ({ leaderboard }) => {
  return (
    <div className="leaderboard">
      <table>
        <thead>
          <tr>
            <th>RANK</th>
            <th>AI MODEL</th>
            <th>WINS</th>
            <th>DRAWS</th>
            <th>LOSSES</th>
            <th>WIN RATE</th>
          </tr>
        </thead>
        <tbody>
          {[...Array(3)].map((_, index) => {
            const entry = leaderboard[index] || {
              id: `empty-${index}`,
              name: '',
              wins: 0,
              draws: 0,
              losses: 0,
              winRate: 0
            };
            
            return (
              <tr key={entry.id}>
                <td>{index + 1}</td>
                <td>{entry.name}</td>
                <td>{entry.wins}</td>
                <td>{entry.draws}</td>
                <td>{entry.losses}</td>
                <td>{`${entry.winRate}%`}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};

export default Leaderboard; 