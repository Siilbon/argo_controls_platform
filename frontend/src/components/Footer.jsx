// Bottom bar shown on every page.
function Footer() {
  return (
    <footer className="border-t border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 px-6 py-4 text-center text-sm text-gray-500 dark:text-gray-400">
      Developed by Karl Siil and Parker Jordan
      <span className="mx-2">·</span>
      <a
        href="https://github.com/Siilbon/argo_controls_platform"
        target="_blank"
        rel="noopener noreferrer"
        className="text-blue-600 dark:text-blue-400 hover:underline"
      >
        GitHub
      </a>
    </footer>
  )
}

export default Footer
