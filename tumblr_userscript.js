// ==UserScript==
// @name         PTO Editing Toolkit
// @locale       English
// @namespace    http://plaintextoffenders.com/
// @version      0.9
// @description  Various tools for PTO editors
// @author       Aviem Zur
// @match        https://www.tumblr.com/*
// ==/UserScript==

var PTO_GOOGLE_CUSTOM_SEARCH_API_KEY = '<PTO_GOOGLE_CUSTOM_SEARCH_API_KEY>';
var PTO_GOOGLE_CUSTOM_SEARCH_ID = '<PTO_GOOGLE_CUSTOM_SEARCH_ID>';

var PTO_FORM_ID = "ptoSearchForm";

checkIsPreviousOffender = function(offender) {
	var xhr = new XMLHttpRequest();
	xhr.onreadystatechange = function() {
	    if (xhr.readyState == XMLHttpRequest.DONE) {
	        var response = JSON.parse(xhr.responseText);
            var totalResults = response.searchInformation.totalResults;
            handleOffenderResult(offender, totalResults);
	    }
	};
    url = 'https://www.googleapis.com/customsearch/v1?key=' + PTO_GOOGLE_CUSTOM_SEARCH_API_KEY + '&cx=' + PTO_GOOGLE_CUSTOM_SEARCH_ID + '&q="' + offender + '"';
    console.log(url);
	xhr.open('GET', url , true);
	xhr.send(null);
};

handleOffenderResult = function(offender, totalResults) {
    var responseNodeId = "ptoResponse";
    var previousResponseNode = document.getElementById(responseNodeId);
    if (previousResponseNode != null) {
        removeNode(previousResponseNode);
    }
    var newResponseNode = null;
    if (totalResults == 0) {
        newResponseNode = document.createElement("DIV");
        newResponseNode.innerText = "Not a previous offender";
        newResponseNode.style.color = "#62bc60";
    } else {
        newResponseNode = document.createElement("A");
        newResponseNode.innerText = "Previous offense found!";
        newResponseNode.href = 'https://www.google.com/search?q="' + offender + '"+site%3Aplaintextoffenders.com';
        newResponseNode.target = "_blank";
        newResponseNode.style.textDecoration = "underline";
        newResponseNode.style.color = "#fc7676";
    }
    newResponseNode.id = responseNodeId;
    getControls().appendChild(newResponseNode);
};

addSearch = function() {
    searchOffender = function() {
        setTimeout(function () {
            var offender = document.getElementById('ptoDomainInput').value.replace(/[, ]*/g, "");
            checkIsPreviousOffender(offender);
        }, 0);
    };
    var form = document.createElement("FORM");
    form.id = PTO_FORM_ID;
    form.innerText = "Offender search:";

    var input = document.createElement("INPUT");
    input.id = "ptoDomainInput";
    input.type = "text";
    input.onpaste = searchOffender;

    form.appendChild(document.createElement("BR"));
    form.appendChild(input);
    getControls().appendChild(form);
    getControls().removeChild(getCloseButton());
};

clickFacebookBtn = function() {
    if (document.getElementsByClassName('facebook checked')[0] == null) {
        document.getElementsByClassName('facebook')[0].firstChild.click();
    }
};

isTwitterChecked = function() {
    return document.getElementsByClassName('twitter checked')[0] != null;
};

changeToAddToQueue = function() {
    document.getElementsByClassName('dropdown-area')[0].click();
    getByXPathSingle('//span[text()="Add to queue"]').click();
    if (!isTwitterChecked()) {
        getActionButton().style.display = "none";
    }
};

fixTweetText = function() {
    var tweetTextArea = document.getElementsByClassName('tweet-textarea')[0];
    if (tweetTextArea != null) {
        expectedText = (/[^\n]*\n.*\n.*\n/.exec(getEditor().innerText)[0].replace('\n\n','\n') + "[URL]").replace(/[ \t]*\[URL\]/,"[URL]");
        tweetTextArea.innerHTML = expectedText;
        tweetTextArea.addEventListener("keyup", function() {
            if (isTwitterChecked()) {
                getActionButton().style.display = "block";
            }
        });
    }
};

alreadyAddedSearch = function() { return document.getElementById(PTO_FORM_ID) != null; };

getByXPathSingle = function(xpath) {
    return getByXPath(xpath).snapshotItem(0);
};

getByXPath = function(xpath) {
    return document.evaluate(xpath,document,null,XPathResult.UNORDERED_NODE_SNAPSHOT_TYPE,null);
};

getControls = function() {
    return document.getElementsByClassName('control left')[1];
};

getCloseButton = function() {
    return document.getElementsByClassName('tx-button')[0];
};

getEditor = function() {
    return document.getElementsByClassName('editor editor-richtext')[0];
};

getActionButton = function() {
    return document.getElementsByClassName('post-form--save-button')[0];
};

removeNode = function(node) {
    node.parentNode.removeChild(node);
};

MutationObserver = window.MutationObserver || window.WebKitMutationObserver;

var observer = new MutationObserver(function(mutations, observer) {
    if (!alreadyAddedSearch()) {
        addSearch();
        clickFacebookBtn();
        changeToAddToQueue();
    }
    fixTweetText();
});

observer.observe(document, {
  subtree: true,
  attributes: true
});
