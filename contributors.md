# Instructions for contributors

![karma avatar](https://user-images.githubusercontent.com/24620154/56662126-952d7f00-66a3-11e9-99b4-924dc6313b2e.png)

So you are interested in playing around with karmabot, maybe trying out new ideas and adding new cool stuff? We invite you to contribute your ideas and projects!

In the following we will outline the main process of how to setup your system to get karmabot up and running.

## Prerequisites

To work on this project and test your bot, you will need the following:

- A Github account: [github.com](https://github.com/)
- An email for joining Slack
- A Python 3 environment with installed pip

## Setting up your development environment

In this section we will describe the steps necessary to seting up your development environment. As we want to program a Slack app (which will be the bot), we need to either create an app or you can use our Slack testing workspace which will provide you with the necessary tokens to authenticate your bot. So follow either the Quickstarting guide for immediate action or the guide that explains to you how to setup things by your own.

### Quickstarting with provided Slack workspace

We have already set up a Slack test workspace with an installed app that your local code can use. 

1. To gain access to the SlackBotTest workspace, use the following invitation link:

   [Join our **SlackBotTest** workspace](https://join.slack.com/t/slackbottest-gruppe/shared_invite/enQtNzg0ODA4MzI5NTkxLTM4NDM0N2I2NDVjZTM0Y2Q1N2JhYTdlOTcxYTNiMGRlMjM1Zjg1YzBiZjUwY2IxYWJmMDIzODRhZmJlMDIzMGM)
   
   Once your have joined the workspace you are allowed to install your apps (bots) and test them as you like with the advantage that, over time, there will hopefully be more people and thus you have more data you can play with.
2. To get the necessary tokens, go into the **#token** channel. There you will find a pinned message with the OAuth Access Token and the Bot User OAtuh Access Token as well as the karmabot UserID.
3. To make the tokens available to your python code, add the two environmental variables
  
   ```shell
   SLACK_KARMA_BOTUSER = <karmabot UserID>
   SLACK_KARMA_TOKEN = <Bot User OAuth Access Token>
   ```

   you obtained from step 2. Environmental variable are a common way to hide sensitive information and credentials from code repositories. The variables are accessed in python in the following way (see the `__init__.py` of the bot subpackage):

   ```python
   botuser = os.environ.get('SLACK_KARMA_BOTUSER')
   token = os.environ.get('SLACK_KARMA_TOKEN')
   ```
   
4. You are ready to start your bot! Go to the root directory of the repository and run `python main.py`. This will start the bot by first authenticating the application to the Slack app and then listening for new messages that start with `@karmabot`. See `main.py` for more details and [Real Time Messaging API](https://api.slack.com/rtm) if you are interested in the rtm api.
5. You can now start to make changes or implement new commands. Just make your code changes and restart the `main.py`. Afterwards, you can go over to the Slack workspace and test your commands.

### Setting up of your own Slack workspace and Slack app

Before we can even start to program we need a few setup steps that involve creating or joining a Slack workspace, creating a Slack App with a new Bot User and finally get the necessary tokens to allow the Slack API to connect with the workspace. All of this will be explained in a minute, so grab a coffee, lean back and follow us down the rabbit hole!

1. The first thing we need is a Slack workspace where we can install our app (which will be a bot in this case). Slack workspaces are free with only a few limitations that do not bother us for programming bots (like a limitation of a channel's history up to 10.000 messages). If you choose this option you have full control over your own workspace and you can add as many apps as you like. You can create your own workspace here, all you need is a email address:

   [Create your own workspace](https://slack.com/create#email)
2. Once you have created your own workspace, you are ready to create your own Slack app and install the app to your workspace. You can start here: [Getting Started](https://api.slack.com/bot-users#getting-started)

   To create your own app, go over to [Your apps](https://api.slack.com/apps) and click the button __Create a Slack App__. Fill in a name for your app and choose a workspace to install the app to. This is the reason why you had to create a workspace previously. The name of your app is not the name of your bot, so feel free to choose any name you like.

   ![Create a Slack App](https://i.imgur.com/C29FV86.png)

   1. Select the **Bots** functionality for your app. This will lead to another dialog for creating your bot user.

   ![Basic information](https://i.imgur.com/OEcEXZM.png)
   2. Fill out the display name and the default username of your bot user. We suggest turning on the option **Always Show My Bot as Online**. Confirm with a click on the button **Add Bot User**. Afterwards, the button text will change to **Save Changes**. You can confirm with another click and you will seen a green "Success" bar at the top of the screen.

   ![Bot User](https://i.imgur.com/EtiGiBO.png)
3. To configure permissions, go over to **Basic Information**. As you can see, we have successfully managed to add the Bots and Permissions features. But wait, when did we actually set any permissions? Indeed, we did not. And this is a common pitfall when setting up your own app: we have to define the scopes the app is allowed to operate in. 

   1. So go over to **Permissions** by clicking on that functionality. 

   ![Basic Information 2](https://i.imgur.com/FWmPr04.png)
   2. You should now be on the page **OAuth & Permissions**. Scroll down to the section **Scopes** where you can select permission scopes your app is allowed to use or call methods from. Add all needed permissions/scopes. Each permission will be added to the list of selected permissions just below the dropdown field. And do not worry: if you miss a critical permission, the `slackclient` Python package will inform you about the missing permission and you can come back any time and add the permission. Confirm with a click on **Save Changes**

   ![Scopes](https://i.imgur.com/9PP1lFC.png)
4. On the same page, scroll back to the top to the section **OAuth Tokens & Redirect URLs**. Here you can finally install the app to your workspace. Just click on **Install App to Workspace**. Next, you have to confirm that you app and bot are granted the selected permissions for your workspace. You can read up the implications of each permission. Confirm the selected permissions. You will be redirected to the **OAuth & Permissions** page.

   ![Install App](https://i.imgur.com/YTdRtnx.png)
5. This time, you should see newly created tokens. These tokens are very important because they allow your Python app to authenticate with the Slack API. All previous steps were necessary to create these tokens. Normally, of course, you do not share these tokens but keep them private. We show them here because this was a test app that will be deleted soon. Because tokens, and any credentials in general, are so sensitive information we won't add them to a repository either. A common practice is to create environmental variables that will hold the token and which we can access in Python via the `os.environment.get()` command.
   ![App Token](https://i.imgur.com/4jTCypC.png)
6. Go to step 3. of the Quickstarting section and follow the instructions there!

## Using the `slackclient` Python package

Now that everything is setup and you have your tokens as well as the environmental variables, you can start using the Slack API! 

You can use all commands that are allowed for bots through the `slackclient` module. A minimal setup looks like

```python
botuser = os.environ.get('SLACK_KARMA_BOTUSER')
token = os.environ.get('SLACK_KARMA_TOKEN')
if not botuser or not token:
    print('Make sure you set SLACK_KARMA_BOTUSER and SLACK_KARMA_TOKEN in env')
    sys.exit(1)

KARMA_BOT = botuser
SLACK_CLIENT = SlackClient(token)
```

Now if you want to retrieve the list of all channels you can use

```python
SLACK_CLIENT.api_call('channels.list', exclude_archived=True, exclude_members=True)
```

As you see, working with the Slack API is as simple as passing the API method to the `api_call()` method. Most API methods support optional arguments like `exclude_archived` and `exclude_members` from the example. For detailed descriptions of all API methods, see [API Methods](https://api.slack.com/methods). 

## Things to watch out for

This documentation is far form being complete and is only a first step in helping new contributors to get along. There are a lot of details that might to be discussed when running into problems with your own Slack workspace or with our SlackBotTest workspace. 

For example:
- The code assumes, that the bot's name is karmabot, which has not to be the case for your bot 
- The id of the **#general** channel is hardcoded in `slack.py` and needs to be changed when you work with this variable for your workspace 
- the user ids of the admins are hardcoded in `slack.py` and need to be changed when you work with these variables for your workspace
