import random
from tensor2tensor.data_generators import problem
from tensor2tensor.data_generators import text_problems
from tensor2tensor.utils import registry

@registry.register_problem
class ObservationPrediction(text_problems.Text2TextProblem):
  """Transduction from observation to prediction."""

  @property
  def approx_vocab_size(self):
    return 2**14  # ~16k

  @property
  def is_generate_per_split(self):
    # generate_data will shard the data into TRAIN and EVAL for us.
    return False

  @property
  def dataset_splits(self):
    """Splits of data to produce and number of output shards for each."""
    # 50% evaluation data
    return [{
        "split": problem.DatasetSplit.TRAIN,
        "shards": 5,
    }, {
        "split": problem.DatasetSplit.EVAL,
        "shards": 5,
    }]

  def generate_samples(self, data_dir, tmp_dir, dataset_split):
    del data_dir
    del tmp_dir
    del dataset_split

    for n in range(10000):
      # wind turbine size factor
      size_factor = random.randint(1, 10)
      # wind speed
      wind_speed = max(0, int(random.gauss(25, 15)))
      # wind turbine power
      turbine_power = int(0.01*size_factor*wind_speed**3)
      yield {
        "inputs": "A_TURBINE with size factor " + repr(size_factor) + " and subjected to windspeed " + repr(wind_speed) + " km/h",
        "targets": "A_TURBINE producing " + repr(turbine_power) + " kW"
      }

      # weight
      weight = max(35, int(random.gauss(62, 20)))
      # height
      height = max(110, int(random.gauss(170, 15)))
      # body mass index
      bmi = int(weight/(height*0.01)**2)
      if bmi < 18:
        bmi_class = "U"
      elif bmi >= 18 and bmi < 25:
        bmi_class = "N"
      elif bmi >= 25 and bmi < 30:
        bmi_class = "O"
      elif bmi >= 30 and bmi < 35:
        bmi_class = "O1"
      elif bmi >= 35 and bmi < 40:
        bmi_class = "O2"
      elif bmi >= 40:
        bmi_class = "O3"
      yield {
        "inputs": "A_PERSON with weight " + repr(weight) + " kg and height " + repr(height) + " cm",
        "targets": "A_PERSON has BMI class " + bmi_class
      }
