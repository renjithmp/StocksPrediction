angular.module('stockApp', ['stockApp.controllers', 'stockApp.directives', 'stockApp.services','ui.router']).config(function ($stateProvider, $httpProvider) {
    'use strict'
    $stateProvider.state('user', {
        url: '/user'
        , templateUrl: 'views/user.html'
        , controller: 'userController'
    });
}).run(function ($state) {
    'use  strict'
    $state.go('user')
});
angular.module('stockApp.controllers', []);
angular.module('stockApp.directives', []);
angular.module('stockApp.services', ['ngResource']);