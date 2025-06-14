module.exports = {
    plugins: [
        require('autoprefixer')({
            overrideBrowserslist: [
                'last 2 versions',
                '> 1%',
                'iOS >= 9',
                'Android >= 4.4'
            ]
        })
    ],
}; 