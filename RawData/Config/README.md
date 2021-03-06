# Configuration

The config files are formatted in the INI format to facilitate their parsing.

First, you have to copy the three files and remove the `.dist` extension.

## Twake

In the `loginTwake` file, you have to write the logins and passwords of your Twake's accounts, formatted as follows. Each entry (beetween brackets) will add an user.
> Note: the login can be the email as well as the Twake username.

```
[Anakin]
login : anakin.skywalker@example.com
password : 1234password
```

## OpenPaas

In the `loginOpenPaas` file, you will similarly write logins and passwords, but you will have to add first and last names as in :

```
[Anakin Skywalker]
mail : anakin.skywalker@example.com
password : 1234password
first_name : Anakin
last_name : Skywalker
```

## Urls

As you may use different SaaS versions of OpenPaas osr Twake, you have to write the urls you are using, ie where the accounts have been created.
The `sitesUrl` file must be filled with these urls, as well as the name of the Twake company (which is also considered as already created). You must also add the name of the Twake Workspace in the language that you use. If you may use both languages, then write both names.
>Note: the urls for the emails and Linshare are the one of their API, where those for Twake and the Calendar are the usual url of the sites.
