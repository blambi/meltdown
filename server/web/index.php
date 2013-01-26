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
    $opts = array(
      'who' => $req->request->get('who'),
      'what' => $req->request->get('what'),
    );

    // Do magic

    return $app->json(array('successful' => true));
});



/* PUTs */
/* Update status of
//$app->put(

/* GETs */
$app->get('/', function() use ($app) {
    return $app->json(
      array(
        array(
          'id' => 41,
          'who' => 'blambi',
          'what' => 'Server X is on fire, called firedepartment',
          'open' => true)));
});



$app->run();
