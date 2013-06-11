# Riff Raff SSH

Reads hosts for the apps you want to track from Riff Raff and writes an SSH
config file for you to the console. Edit `config.yml.new` then rename it
`config.yml` and you're good to go.

## config.yml

You need these keys:

* `api_key` - your Riff Raff API key
* `apps` - a list of app names (as defined in
  [Riff Raff hosts](https://dev.riffraff.gudev.gnl/deployinfo/hosts))
  
These are optional:

* `app_name_rewrites` - by default, the name of the app is used as the host
  name in your SSH config - you can supply a map of more concise names here;
* `extra_params` - allows you to define extra parameters to be appended to
  entries by app and stage. An obvious one to supply is User.
  
### Extra Params

Extra params is a list of rules represented as maps with the following keys:

* `apps` - either a list of apps for which this applies or the "*" string,
  meaning apply this rule to all apps;
* `stages` - either a list of stages as defined in Riff Raff (e.g. "PROD") or
  the "*" string, meaning apply this rule for all stages;
* `params` - a map of the SSH config params to include.

Later rules take precedence.

### Example config

See `example_config.yml`.

## Static config

If you have a chunk of SSH config you'd like to include with the generated
config, create a file in the script's directory called `static_config` with
the entries. 

## Dependencies

* Python
* yaml module
* requests module




