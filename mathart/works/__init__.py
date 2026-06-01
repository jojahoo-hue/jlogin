from . import misty_forest, wind_turbines, running_horse, wind_turbines_exact

REGISTRY = {
    "forest": misty_forest.render,
    "turbines": wind_turbines.render,
    "horse": running_horse.render,
    "turbines-exact": wind_turbines_exact.render,
}
