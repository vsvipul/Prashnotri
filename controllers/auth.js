var passport = require('passport');
var account = require('../models/account');

exports.postRegister = function(req, res){
    var acc = new account({
        username: req.body.username,
        email: req.body.email,
        name: req.body.name,
        city: req.body.city,
        phone: req.body.phone
    });
    account.register(acc, req.body.password, function(err, user){
        if (err){
            return res.render('register', {user: user});
        }
        passport.authenticate('local')(req, res, function(){
            res.redirect('/');
        });
    });
};

exports.getLogin = function(req, res){
    if (req.user){
        res.render('login', {message: "You have already logged in"});
    }
    else{
        res.render('login',{user: null, message: null});
    }
};

exports.postLogin = function(req, res){
    passport.authenticate('local', function(err, user){
        if (!user){
            return res.render('login', {message: "Wrong username or password"});
        }
        req.logIn(user, function(err){
            if (err){
                console.log(err);
                return res.render('login', {message: "Wrong username or password"});
            }
            return res.redirect('/');
        });
    })(req,res);
};

exports.updateProfile = function(req, res){
    var acc = {
        email: req.body.email,
        name: req.body.name,
        city: req.body.city,
        phone: req.body.phone
    };
    account.findOneAndUpdate({username: req.user.username}, acc, function(err, result){
        if(err){
            console.log(err);
        }
        // console.log("RESULT: " + result);
        return res.redirect('profile');
    });

};

exports.getLogout = function(req, res){
    req.logout();
    res.redirect('/');
}