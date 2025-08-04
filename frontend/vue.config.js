const path = require('path')

function getOutputDir() {
    switch (process.env.NODE_ENV) {
      case 'production': return '../backend/templates'
      case 'dev': return 'dist'
      default: return 'dist'
    }
  }

  function getAssetsDir() {
    switch (process.env.NODE_ENV) {
      case 'production': return '../static'
      case 'dev': return ''
      default: return ''
    }
  }
  
  module.exports = {
    outputDir: getOutputDir(),
    assetsDir: getAssetsDir(),
  }
