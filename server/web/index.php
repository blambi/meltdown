<?php
require_once __DIR__.'/../vendor/autoload.php';
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\ParameterBag;

$app = new Silex\Application();

/* - Pick out the JSON - */
$app->before(function (Request $request){
    if (0 === strpos($request->headers->get('content-type'), 'application/json')) {
      $data = json_decode($request->getContent(), true);
      $request->request->replace(is_array($data) ? $data : array());
      $request->is_json = TRUE;
    }
    else {
      $request->is_json = FALSE;
    }
});

/*
  Issue objects should look something like this:

  ID   - autoincr int
  who  - string
  what - longer string.
  Date - unix timestamp
  Open - Boolean
*/

/* POSTs */
/* New status post */
$app->post('/', function(Request $req) use ($app) {
    // Arguments
    $who = $req->request->get('who');
    $what = $req->request->get('what');

    if(empty($who) or empty($what)) {
      return $app->json(array('success' => false,
                              'why' => 'To few arguments'), 418);
    }

    $mongo = new \Mongo();
    $db = $mongo->meltdown;

    // Generate next id
    $uid_obj = $db->variables->findOne(array('name' => 'uid_counter'), array('value' => -1));
    $uid = !empty($uid_obj) && key_exists('value', $uid_obj) ? $uid_obj['value'] +1 : 0;
    $db->variables->remove(array('name' => 'uid_counter'));
    $db->variables->insert(array('name' => 'uid_counter', 'value' => $uid));

    $db->issues->insert(array(
                            '_id' => $uid,
                            'who' => strip_tags($who),
                            'what' => strip_tags($what),
                            'date' => time(),
                            'open' => true,
    ));

    return $app->json(array('success' => true, 'id' => $uid), 201);
});


/**
 * PUTs
 * Are used for updating or closing issues
 */
$app->put('/{id}/close', function($id) use ($app) {
    if(!(is_numeric($id) && is_int((int)$id))) {
      return $app->json(array('success' => false, 'why' => "Issue ID must be an INT"), 418);
    }

    $mongo = new \Mongo();
    $db = $mongo->meltdown;

    // db.issues.update({'_id': 1},{$set: {'open': false}});
    $db->issues->update(array('_id' => (int)$id), array('$set' => array('open' => false)));
    $issue = $db->issues->findOne(array('_id' => (int)$id));

    if(isset($issue) && !$issue['open']) { // add isset $issue
      return $app->json(array('success' => true, 'open' => $issue['open'], 'id' => $issue['_id']), 200);
    }

    return $app->json(array('success' => false, 'why' => "Update failed"), 500);
});

/**
 * Update
 */
$app->put('/{id}', function(Request $req, $id) use ($app) {
    if (!$req->is_json) {
      return $app->json(array('success' => false, 'why' => "json body required"), 418);
    }

    // 1. If ID is ok
    if(!(is_numeric($id) && is_int((int)$id))) {
      return $app->json(array('success' => false, 'why' => "Issue ID must be an INT"), 418);
    }

    // 2. Check we got either: who or what
    $updates = array(
      'who' => $req->request->get('who'),
      'what' => $req->request->get('what'),
    );

    if(empty($updates['who'])) {
      unset($updates['who']);
    }
    if(empty($updates['what'])) {
      unset($updates['what']);
    }

    if(count($updates) == 0) {
      return $app->json(array('success' => false,
                              'why' => 'Neither who or what specified'), 418);
    }

    $mongo = new \Mongo();
    $db = $mongo->meltdown;

    // 3. update
    $db->issues->update(array('_id' => (int)$id), array('$set' => $updates));
    $issue = $db->issues->findOne(array('_id' => (int)$id));

    if(isset($issue)) { // add isset $issue
      return $app->json(array('success' => true, 'issue' => $issue, 'id' => $issue['_id']), 200);
    }
    else {
      return $app->json(array('success' => false, 'why' => "Unknown ID"), 418);
    }
});

$app->put('/{id}/comment', function($id) use ($app) {


});

/* GETs */
$app->get('/', function(Request $req) use ($app) {
    $mongo = new \Mongo();
    $db = $mongo->meltdown;
    $open_issues = $db->issues->find(array('open' => true));

    if ($req->is_json) {
      $ret = array();
      foreach($open_issues as $issue) {
        $ret[]= array(
          'id' => $issue['_id'],
          'who' => $issue['who'],
          'what' => $issue['what'],
          'date' => $issue['date'],
          'open' => $issue['open']);
      }

      return $app->json($ret);
    }
    else {
        $ret = "Open issues:\n";

        foreach($open_issues as $issue) {
          $num = "[". $issue['_id'] . "] ";
          $indent = ''; // There must be a nicer way...
          for($x=0; $x<strlen($num); $x++) {
            $indent .= ' ';
          }
          $ret .= $num . $issue['what'] . "\n" . $indent . "who: " . $issue['who'] . "\n" . $indent . "date: " . date('c', $issue['date']) . "\n\n";
        }

        return new Response($ret, 200, array('Content-Type' => 'text/plain'));
    }
});

$app->get('/{id}', function(Request $req, $id) use ($app) {
    if(!(is_numeric($id) && is_int((int)$id))) {
      return $app->json(array('success' => false, 'why' => "Issue ID must be an INT"), 418);
    }

    $mongo = new \Mongo();
    $db = $mongo->meltdown;
    $issue = $db->issues->findOne(array('_id' => (int)$id));

    if (empty($issue)) {
      if (!$req->is_json) {
        return new Response("No such issue.", 404, array('Content-Type' => 'text/plain'));
      }
      else {
        return $app->json(array('success' => false, 'why' => "No such issue"), 404);
      }
    }

    if ($req->is_json) {
      return $app->json(array(
          'id' => $issue['_id'],
          'who' => $issue['who'],
          'what' => $issue['what'],
          'date' => $issue['date'],
          'open' => $issue['open'])
      );
    }
    else {
      $ret = "[". $issue['_id'] . "] who: " . $issue['who'] . ", what: " .
        $issue['what'] . ", date: " . $issue['date']. "\n";
      return new Response($ret, 200, array('Content-Type' => 'text/plain'));
    }
});


$app->run();
