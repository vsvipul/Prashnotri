var express = require('express');
var router = express.Router();

var authController = require('../controllers/auth');
var indexController = require('../controllers/index');

router.get('/', indexController.getIndex);

router.get('/login', authController.getLogin);

router.post('/login', authController.postLogin);

router.get('/logout', authController.getLogout);

router.get('/register', function(req, res) {
    res.render('register');
});

router.post('/register', authController.postRegister);

router.get('/addquiz', function(req, res) {
    res.render('addquiz', {user: req.user});
});

router.get('/about', function(req, res) {
    res.render('about', {user: req.user});
});

module.exports = router;