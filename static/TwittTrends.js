var locations = null;
var text = null;
var user = null;
var live = null;
var olddata;
var socket;
var keyword, selected;
var marker, tweet;
var markerSet = new Array();
var positive_green_icon = 'http://maps.google.com/mapfiles/ms/icons/green-dot.png';
var neutral_yellow_icon = 'http://maps.google.com/mapfiles/ms/icons/yellow-dot.png';
var negative_purple_icon = 'http://maps.google.com/mapfiles/ms/icons/purple-dot.png';
var sentiment_icons_set = {"positive": positive_green_icon, "neutral": neutral_yellow_icon, "negative": negative_purple_icon}
var infowindow = new google.maps.InfoWindow();
var map = new google.maps.Map(document.getElementById('map'), {
    zoom: 3,
    center: new google.maps.LatLng(40.8, -73.96),
    mapTypeId: google.maps.MapTypeId.ROADMAP
});


$('#refresh').on('click', function() {
    clearMap();
});


$('#start').on('click', function() {
    //socket = io.connect('http://' + document.domain + ':' + location.port + '/live');
    socket = io.connect('http://' + document.domain + '/live');
    console.log("Start Live Streaming!");

    socket.on('livetweet', function(data) {
        keyword = data.keyword;
        if (selected != $("#tags option:selected").val()) {
            clearMap();
        }
        selected = $("#tags option:selected").val();
        console.log("Incoming keyword: " + keyword, "Selected keyword: " + selected)
        if (keyword == selected) {
            locations = data.coordinates;
            console.log(locations);
            text = data.text;
            console.log(text);
            user = data.author;
            console.log(user);
            sentiment = data.sentiment;
            console.log(sentiment);
            plotLiveMarkers(locations, text, user, sentiment);
        } else if (selected == "All") {
            locations = data.coordinates;
            console.log(locations);
            text = data.text;
            console.log(text);
            user = data.author;
            console.log(user);
            sentiment = data.sentiment;
            console.log(sentiment);
            plotLiveMarkers(locations, text, user, sentiment);
        } else {
            console.log("Different keywords! Pass");
        }
    });
});


$('#stop').on('click', function() {
    socket.disconnect();
    console.log("Stop Live Streaming!");
})


$('#search').on('click', searchkeyword);


function searchkeyword(){
    $.ajax({
        type: 'POST',
        url: '/keyword',
        data:
        {
            "tags": $("#tags option:selected").val()
        },
        dataType: 'json',
        success: function(data) {
            console.log('Keyword! Backend to Frontend!');      
            locations = data.locs;
            console.log(locations);
            text = data.text;
            console.log(text);
            user = data.user;
            console.log(user);
            sentiment = data.sentiment;
            console.log(sentiment);
            
            clearMap();

            plotMarkers(locations, text, user, sentiment);
        },
        error: function() {
            console.log('Error!');
        }
    });
};


google.maps.event.addListener(map, 'click', function(event) {
    clearMap();
    
    var lat = event.latLng.lat();
    var lng = event.latLng.lng();
 
    var image = 'https://developers.google.com/maps/documentation/javascript/examples/full/images/beachflag.png'; 
    marker = new google.maps.Marker({
        position: {lat: lat, lng: lng},
        map: map,
        icon: image,
        clickable: true
    });

    marker.info = new google.maps.InfoWindow({
        content: lat.toString() + ', ' + lng.toString()
    });

    google.maps.event.addListener(marker, 'click', function() {
        marker.info.open(map, marker);
    });

    $.getJSON('/local', {
        lat: lat,
        lng: lng
    }, function(data) {
        console.log("Click! Backend to Frontend!")
        locations = data.locs;
        console.log(locations);
        text = data.text;
        console.log(text);
        user = data.user;
        console.log(user);
        sentiment = data.sentiment;
        console.log(sentiment);

        plotMarkers(locations, text, user, sentiment);
    });
    return false;
});


function clearMap() {
    if (marker) {
        marker.setMap(null);
    }
    
    if (markerSet) {
        if (markerSet.length > 0) {
            for (var i = 0; i < markerSet.length; i++) {
                markerSet[i].setMap(null);
            }
        }
    }
};


function plotLiveMarkers(locations, text, user, sentiment) {
    var latLng = new google.maps.LatLng(locations[1], locations[0]);
    var tweet = new google.maps.Marker({
        position: latLng,
        map: map,
        icon: sentiment_icons_set[sentiment]
    });
    console.log(tweet);
    google.maps.event.addListener(tweet, 'click', (function(tweet) {
        return function() {
            infowindow.setContent('<b>' + sentiment + '</b>' + ' ' + '@' + user +': ' + '<b>' + text + '</b>');
            infowindow.open(map, tweet);
        }
    })(tweet));
    markerSet.push(tweet);
};


function plotMarkers(locations, text, user, sentiment) {
    for (var i = 0; i < locations.length; i++) {
        var latLng = new google.maps.LatLng(locations[i][0], locations[i][1]);
        var tweet = new google.maps.Marker({
            position: latLng,
            map: map,
            icon: sentiment_icons_set[sentiment[i]]
        });
        console.log(tweet)
        google.maps.event.addListener(tweet, 'click', (function(tweet, i) {
            return function() {
                infowindow.setContent('<b>' + sentiment[i] + '</b>' + ' ' + '@' + user[i] +': ' + '<b>' + text[i] + '</b>');
                infowindow.open(map, tweet);
            }
        })(tweet, i));
        markerSet.push(tweet);
    }
};

