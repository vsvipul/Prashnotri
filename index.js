var config = require('./config');
var express = require('express');
var bodyParser = require('body-parser');
var cookieParser = require('cookie-parser');
var mongoose = require('mongoose');
var passport = require('passport');
var localStrategy = require('passport-local').Strategy;
var expressSession = require('express-session');

var port = process.env.PORT || config.serverPort;
var sessionSecret = process.env.SESSION_SECRET || config.sessionSecret;
var db_user = process.env.DB_USER || config.db_user;
var db_pass = process.env.DB_PASS || config.db_pass;
var connectionString = process.env.DB_STR || config.connectionString;

var app = express();

console.log(connectionString);
mongoose.connect(connectionString, {useNewUrlParser: true});

var server = app.listen(port, () => {
    console.log("Listening on port " + port);
});

app.use(express.static('public'));
app.use(bodyParser.urlencoded({extended: true}));
app.use(bodyParser.json());
app.use(cookieParser());
app.use(expressSession({
    secret: sessionSecret,
    resave: false,
    saveUninitialized: false
}));

app.use(passport.initialize());
app.use(passport.session());

app.set('view engine', 'ejs');

var account = require('./models/account');
passport.use(new localStrategy(account.authenticate()));
passport.serializeUser(account.serializeUser());
passport.deserializeUser(account.deserializeUser());

var indexRoute = require('./routes/index');

app.use('/', indexRoute);