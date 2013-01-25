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

/* GETs */
$app->get('/', function() use ($app) {
    return 'Hello '.$app->escape($name);
});

$app->get('/list.json', function() use ($app) {
    return $app->json(array(array(
                              'id' => 41,
                              'who' => 'blambi',
                              'what' => 'Server X is on fire, called firedepartment',
                              'open' => true )));
});



$app->run();
