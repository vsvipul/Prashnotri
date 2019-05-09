
exports.getIndex = function(req, res){
    res.render('index', {
        user: req.user
    });
};
