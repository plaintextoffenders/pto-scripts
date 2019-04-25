// ==UserScript==
// @name         PTO Editing Toolkit
// @locale       English
// @namespace    http://plaintextoffenders.com/
// @version      0.14
// @description  Various tools for PTO editors
// @author       Aviem Zur
// @match        https://www.tumblr.com/*
// ==/UserScript==

var PTO_FORM_ID = "ptoSearchForm";

var previousOffenders = '';
var reformedOffenders = '';

window.checkIsPreviousOffender = function(offender) {
    if (previousOffenders == '') {
        window.loadGitHubData('offenders', offender);
    }
    if (reformedOffenders == '') {
        window.loadGitHubData('reformed', offender);
    }
    if (reformedOffenders != '' && previousOffenders != '') {
        window.handleOffenderResult(offender);
    }
};

window.loadGitHubData = function(csvName, offender) {
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
        if (xhr.readyState == XMLHttpRequest.DONE) {
            if (xhr.responseText.length > 1000) {
                if (csvName == 'offenders') {
                    previousOffenders = xhr.responseText;
                }
                if (csvName == 'reformed') {
                    reformedOffenders = xhr.responseText;
                }
                if (offender != '') {
                    window.handleOffenderResult(offender);
                }
            } else {
                if (offender != '') {
                    window.checkIsPreviousOffender(offender);
                }
            }
        }
    };
    var url = 'https://raw.githubusercontent.com/plaintextoffenders/plaintextoffenders/master/' + csvName + '.csv';
    console.log(url);
    xhr.open('GET', url , true);
    xhr.send(null);
}

window.handleOffenderResult = function(offender) {
    var responseNodeId = "ptoResponse";
    var previousResponseNode = document.getElementById(responseNodeId);
    if (previousResponseNode != null) {
        window.removeNode(previousResponseNode);
    }
    var newResponseNode = null;
    if (previousOffenders.includes(offender) || reformedOffenders.includes(offender)) {
        newResponseNode = document.createElement("A");
        newResponseNode.innerText = "Previous offense found!";
        newResponseNode.href = 'https://github.com/plaintextoffenders/plaintextoffenders';
        newResponseNode.target = "_blank";
        newResponseNode.style.textDecoration = "underline";
        newResponseNode.style.color = "#fc7676";
    } else {
        newResponseNode = document.createElement("DIV");
        newResponseNode.innerText = "Not a previous offender";
        newResponseNode.style.color = "#62bc60";
    }
    newResponseNode.id = responseNodeId;
    window.getControls().appendChild(newResponseNode);
};

window.addSearch = function() {
    var searchOffender = function() {
        setTimeout(function () {
            var offender = document.getElementById('ptoDomainInput').value.replace(/[, ]*/g, "");
            window.checkIsPreviousOffender(offender);
        }, 0);
    };
    var form = document.createElement("FORM");
    form.id = PTO_FORM_ID;
    form.innerText = "Offender search:";

    var input = document.createElement("INPUT");
    input.id = "ptoDomainInput";
    input.type = "text";
    input.onkeyup = searchOffender;

    form.appendChild(document.createElement("BR"));
    form.appendChild(input);
    window.getControls().appendChild(form);
    window.getControls().removeChild(window.getCloseButton());
};

window.clickFacebookBtn = function() {
    if (document.getElementsByClassName('facebook checked')[0] == null) {
        document.getElementsByClassName('facebook')[0].firstChild.click();
    }
};

window.isTwitterChecked = function() {
    return document.getElementsByClassName('twitter checked')[0] != null;
};

window.changeToAddToQueue = function() {
    document.getElementsByClassName('dropdown-area')[0].click();
    window.getByXPathSingle('//span[text()="Add to queue"]').click();
    if (!window.isTwitterChecked()) {
        window.getActionButton().style.display = "none";
    }
};

window.fixTweetText = function() {
    var tweetTextArea = document.getElementsByClassName('tweet-textarea')[0];
    if (tweetTextArea != null) {
        var expectedText = (/[^\n]*\n.*\n.*\n/.exec(window.getEditor().innerText)[0].replace('\n\n','\n') + "[URL]").replace(/[ \t]*\[URL\]/,"[URL]");
        tweetTextArea.innerHTML = expectedText;
        tweetTextArea.addEventListener("keyup", function() {
            if (window.isTwitterChecked()) {
                window.getActionButton().style.display = "block";
            }
        });
    }
};

window.alreadyAddedSearch = function() {
    return document.getElementById(PTO_FORM_ID) != null;
};

window.getByXPathSingle = function(xpath) {
    return window.getByXPath(xpath).snapshotItem(0);
};

window.getByXPath = function(xpath) {
    return document.evaluate(xpath,document,null,XPathResult.UNORDERED_NODE_SNAPSHOT_TYPE,null);
};

window.getControls = function() {
    return document.getElementsByClassName('control left')[1];
};

window.getCloseButton = function() {
    return document.getElementsByClassName('tx-button')[0];
};

window.getEditor = function() {
    return document.getElementsByClassName('editor editor-richtext')[0];
};

window.getActionButton = function() {
    return document.getElementsByClassName('post-form--save-button')[0];
};

window.removeNode = function(node) {
    node.parentNode.removeChild(node);
};

window.addDomainsLine = function() {
    var editor = window.getEditor();
    var editorText = editor.innerHTML;
    var domains = window.getDomainsFromString(editorText);
    if (domains.length > 0) {
        editor.innerHTML = '<p>' + domains.join(', ') + '</p>' + editor.innerHTML;
        document.getElementById('ptoDomainInput').value = domains[0];
        window.checkIsPreviousOffender(domains[0]);
    }
}

window.badDomainPrefixes = ['www.', 'http://', 'https://']

window.getDomainsFromString = function(str) {
	var res = new Set();

	var re1 = /(?=[^a-zA-Z0-9]([a-zA-Z0-9]+\.[a-zA-Z0-9]+))/g;
	var re2 = /(?=[^a-zA-Z0-9]([a-zA-Z0-9]+\.[a-zA-Z0-9]+\.[a-zA-Z0-9]+))/g;
	str.replace(re1, function(match, g1, g2) { res.add(g1.toLowerCase()); });
	str.replace(re2, function(match, g1, g2) { res.add(g1.toLowerCase()); });

	res = new Set([...res].filter(function(s) {
		for (let prefix of window.badDomainPrefixes) {
			if (s.startsWith(prefix)) {
				return false;
			}
		}
		return true;
	}));

	for (let result of res) {
		for (let result2 of res) {
			if (result != result2 && result.includes(result2)) {
                console.log(result2);
				res.delete(result2);
			}
		}
	}

    return [...res];
}

var offender = '';
window.loadGitHubData('offenders', offender);
window.loadGitHubData('reformed', offender);

MutationObserver = window.MutationObserver || window.WebKitMutationObserver;

var observer = new MutationObserver(function(mutations, observer) {
    if (!window.alreadyAddedSearch()) {
        window.addSearch();
        window.addDomainsLine();
        window.changeToAddToQueue();
        //window.clickFacebookBtn();
    }
    window.fixTweetText();
});

observer.observe(document, {
  subtree: true,
  attributes: true
});
