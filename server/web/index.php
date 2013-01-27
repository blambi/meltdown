<?php
require_once __DIR__.'/../vendor/autoload.php';
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\ParameterBag;

$app = new Silex\Application();

/* - Pick out the JSON - */
$app->before(function (Request $request){
    if (0 === strpos($request->headers->get('Content-Type'), 'application/json')) {
      $data = json_decode($request->getContent(), true);
      $request->request->replace(is_array($data) ? $data : array());
    }
});

/*
  Issue objects should look something like this:

  ID   - autoincr int
  who  - string
  what - longer string.
  Open - Boolean
*/

/* POSTs */
/* New status post */
$app->post('/', function(Request $req) use ($app) {
    // Arguments
    $who = $req->request->get('who');
    $what = $req->request->get('what');

    /*if(empty($opts['who']) or empty($opts['what'])) {
      return $app->json(array('success' => false,
                              'message' => 'To few arguments'));
                              }*/

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
                          'what' => strip_tags($what)));

    return $app->json(array('successful' => true, 'id' => $uid));
});



/* PUTs */
/* Update status of
//$app->put(

/* GETs */
$app->get('/', function(Request $req) use ($app) {
    if (0 === strpos($req->headers->get('Content-Type'), 'application/json')) {
      return $app->json(
        array(
          array(
            'id' => 41,
            'who' => 'blambi',
            'what' => 'Server X is on fire, called firedepartment',
            'open' => true)));
    }
    else {
        return "not yet...";
    }
});



$app->run();
