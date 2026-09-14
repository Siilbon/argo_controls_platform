import { useState } from 'react'

// Props:
//   title       - card heading
//   description - subtitle text
//   placeholder - input hint text
//   onSearch    - function called with the search string when the form is submitted
function SearchCard({ title, description, placeholder, onSearch }) {
  // useState gives this component its own local variable.
  // [value, setValue] — value is the current state, setValue updates it.
  // Every time setValue is called React re-renders just this component.
  const [value, setValue] = useState('')

  function handleSubmit(e) {
    e.preventDefault()           // stop the browser from reloading the page
    if (value.trim()) onSearch(value.trim())
  }

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
      <h2 className="text-xl font-semibold text-gray-800 mb-1">{title}</h2>
      <p className="text-sm text-gray-500 mb-4">{description}</p>
      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          type="text"
          value={value}
          onChange={e => setValue(e.target.value)}
          placeholder={placeholder}
          // min-w-0 lets the input shrink below its built-in ~20 character
          // width, so the button stays inside narrow cards
          className="flex-1 min-w-0 border border-gray-300 rounded-lg px-3 py-2 text-sm
                     focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          type="submit"
          className="shrink-0 bg-blue-600 text-white px-4 py-2 rounded-lg text-sm
                     hover:bg-blue-700 transition-colors"
        >
          Search
        </button>
      </form>
    </div>
  )
}

export default SearchCard
