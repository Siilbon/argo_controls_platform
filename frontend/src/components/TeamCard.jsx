// A purely presentational component — no state, just renders what it receives.
// Props:
//   member - { name, role, email, linkedin, units: string[] }
function TeamCard({ member }) {
  return (
    <div className="bg-white rounded-3xl shadow-sm border border-gray-200 p-5 flex flex-col gap-2">
      <div>
        {member.email ? (
          <a
            href={`mailto:${member.email}`}
            className="text-base font-semibold text-blue-700 hover:underline"
          >
            {member.name}
          </a>
        ) : (
          <span className="text-base font-semibold text-gray-800">{member.name}</span>
        )}
        <p className="text-sm text-gray-600">{member.role}</p>
      </div>

      {member.units.length > 0 && (
        <div className="flex flex-wrap gap-1 mt-1">
          {member.units.map(unit => (
            <span
              key={unit}
              className="text-xs bg-blue-50 text-blue-600 px-2 py-0.5 rounded-full"
            >
              {unit}
            </span>
          ))}
        </div>
      )}

      {member.linkedin && (
        <a
          href={member.linkedin}
          target="_blank"
          rel="noreferrer"
          className="text-xs text-gray-400 hover:text-blue-500 mt-auto"
        >
          LinkedIn →
        </a>
      )}
    </div>
  )
}

export default TeamCard
