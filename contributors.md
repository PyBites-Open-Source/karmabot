# Instructions for contributors

![karma avatar](https://user-images.githubusercontent.com/24620154/56662126-952d7f00-66a3-11e9-99b4-924dc6313b2e.png)

So you are interested in playing around with karmabot, maybe trying out new ideas and adding new cool stuff? We invite you to contribute your ideas and projects!

In the following we will outline the main process of how to setup your system to get karmabot up and running.

## Prerequisites

To work on this project and test your bot, you will need the following:

- A Github account: [github.com](https://github.com/)
- An email for joining Slack
- A Python 3 environment with installed pip

## Create your own workspace or join our test workspace

Before we can even start to program we need a few setup steps that involve creating or joining a Slack workspace, creating a Slack App with a new Bot User and finally get the necessary tokens to allow the Slack API to connect with the workspace. All of this will be explained in a minute, so grab a coffee, lean back and follow us down the rabbit hole!

The first thing we need is a Slack workspace where we can install our app (which will be a bot in this case). You have two options:

- Create your own workspace. Slack workspaces are free with only a few limitations that do not bother us for programming bots (like a limitation of a channel's history up to 10.000 messages). If you choose this option you have full control over your own workspace and you can add as many apps as you like. You can create your own workspace here, all you need is a email address:

  [Create your own workspace](https://slack.com/create#email)

- Instead of creating your own workspace, you can join our test workspace where we will allow you to install your apps (bots) and play around with the advantage that over time we will be more people and thus have more data you can play around with. We will provide you with the tokens you need once you have joined the workspace. To join our workspace you can use the following invitation link:

  [Join our **SlackBotTest** workspace](https://join.slack.com/t/slackbottest-gruppe/shared_invite/enQtNzg0ODA4MzI5NTkxLTM4NDM0N2I2NDVjZTM0Y2Q1N2JhYTdlOTcxYTNiMGRlMjM1Zjg1YzBiZjUwY2IxYWJmMDIzODRhZmJlMDIzMGM)

## Create your own app or use the provided app

Because we are programming bots for Slack, we need a way to communicate with a Slack workspace. 

### Create a new app and a bot user

Once you have created your own workspace, you are ready to create your own Slack app and install the app to your workspace. 

You can start here: [Getting Started](https://api.slack.com/bot-users#getting-started)

1. Go over to [Your apps](https://api.slack.com/apps) and click the button __Create a Slack App__. Fill in a name for your app and choose a workspace to install the app to. This is the reason why you had to create a workspace previously. The name of your app is not the name of your bot, so feel free to choose any name you like.

  ![Create a Slack App](https://i.imgur.com/C29FV86.png)

2. Select the **Bots** functionality for your app. This will lead to another dialog for creating your bot user.

  ![Basic information](https://i.imgur.com/OEcEXZM.png)

3. Fill out the display name and the default username of your bot user. We suggest turning on the option **Always Show My Bot as Online**. Confirm with a click on the button **Add Bot User**. Afterwards, the button text will change to **Save Changes**. You can confirm with another click and you will seen a green "Success" bar at the top of the screen.

  ![Bot User](https://i.imgur.com/EtiGiBO.png)

4. Configure permissions. Go over to **Basic Information**. As you can see, we have successfully managed to add the Bots and Permissions features. But wait, when did we actually set any permissions? Indeed, we did not. And this is a common pitfall when setting up your own app: we have to define the scopes the app is allowed to operate in. So go over to **Permissions** by clicking on that functionality. 

  ![Basic Information 2](https://i.imgur.com/FWmPr04.png)

5. You should now be on the page **OAuth & Permissions**. Sroll down to the section **Scopes** where you can select permission scopes you app is allowed to use or call methods from. Add all needed permissions/scopes. Each permission will be added to the list of selected permissions just below the dropdown field. And do not worry: if you miss a critical permission, the `slackclient` Python package will inform you about the missing permission and you can come back any time and add the permission. Confirm with a click on **Save Changes**

  ![Scopes](https://i.imgur.com/9PP1lFC.png)

6. On the same page, scroll back to the top to the section **OAuth Tokens & Redirect URLs**. Here you can finally install the app to your workspace. Just click on **Install App to Workspace**. Next, you have to confirm that you app and bot are granted the selected permissions for your workspace. You can read up the implications of each permission. Confirm the selected permissions. 

  ![Install App](https://i.imgur.com/YTdRtnx.png)

7. You will be redirected to the **OAuth & Permissions** page. This time, you should see newly created tokens. These tokens are very important because they allow your Python app to authenticate with the Slack API. All previous steps were necessary to create these tokens. Normally, of course, you do not share these tokens but keep them private. We show them here because this was a test app that will be deleted soon. Because tokens, and any credentials in general, are so sensitive information we won't add them to a repository either. A common practice is to create environmental variables that will hold the token and which we can access in Python via the `os.environment.get()` command.

  ![App Token](https://i.imgur.com/4jTCypC.png)

### Use our provided karmabot test app


