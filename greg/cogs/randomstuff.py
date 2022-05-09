"""Everything cog"""
import random

from ._utils import *


class RandomStuff(Cog):
    """Commands and event handlers for polls"""

    @command()
    async def quote(self, ctx):
        """returns a random quote from the 2358 quotes pages"""
        quotes = ['Do as I say, NOT as I do', 'Arnold Schwarzenegger: half motor oil, half anti-freeze',
                  'It\'s only communism when I say it\'s communism']
        a = ['\"I\'m hungy, I\'m gonna go eat my cookie\"',
             '\"Yo I didn\'t know you guys kept gatorade in here!\" * grabs windex *',
             '\"I don\'t have insomnia I just can\'t sleep at night\"']
        b = ['\"I have to bark back or else it feels awkward\"',
             '\"Though I\'m pretty they don\'t have to do anything\"',
             '\"Okay who nominated Mr. Beast\"']
        c = ['\"My brain is a code.org assignment\"', '\"Did Carl Sagan write the Communist Manifesto?\"',
             '\"Diaphragm\" (pronounced as spelled)', '\"I thought Apple Bottom Jeans was a song from the forties\"']
        d = ['\"Did you know about the surgery they used to do for Cadillacs\"',
             '\"Using discord light mode is Adrian\'s only personality trait\"', '\"Explain this, Santa deniers\"']
        e = ['\"Joe Biden isn\'t black\"', '\"Why is there Al Gore Fanfiction?\"', '\"Work fast safety last!\"',
             '\"This club is NOT a safe space for left handed people\"']
        f = ['\"Y\'know what\'s fun? Arson\"', '\"It\'s like using a nuclear bomb to kill a spider in your house\"',
             '\"Who sells communist fan merch?\"']
        quotes.extend(a)
        quotes.extend(b)
        quotes.extend(c)
        quotes.extend(d)
        quotes.extend(e)
        quotes.extend(f)
        names = ['-Abraham Lincoln', '-Barack Obama', '-George Washington', '-Sun Tzu', '-Winston Churchill',
                 '-Franklin Delano Roosevelt', '-Confucius', '-Dwayne \"The Rock\" Johnson', '-Socrates', '-John Locke']
        g = ['-William Shakespeare']
        names.extend(g)
        quote = random.choice(quotes)
        name = random.choice(names)
        await ctx.send(quote + '\n' + '\n' + name)
        return

    @command()
    async def drawcard(self, ctx):
        """returns a random card value"""
        card_names = ['Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten', 'Jack', 'Queen', 'King',
                      'Ace']
        suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
        card = random.choice(card_names)
        suit = random.choice(suits)
        await ctx.send('Your card is the ' + card + ' of ' + suit + '!')
        return

    @command()
    async def newpoll(self, ctx, *, pollname):
        erase_1 = open('ResultStore1.txt', 'w')
        erase_2 = open('ResultStore2.txt', 'w')
        pollname = ''
        await ctx.send(
            f'**NEW POLL** \n \n{pollname}\n \nSend "{ctx.prefix}vote Y" to vote yes and "{ctx.prefix}vote N" to vote '
            f'no. I will confirm that your vote has been received in chat. You *can* change your vote later if you so '
            f'wish')

    @command()
    async def getresults(self, ctx, ):
        votecounts = [0, 0]
        key_1 = 'ResultStore1.txt'
        key_2 = 'ResultStore2.txt'
        f1 = open(key_1, 'r')
        f2 = open(key_2, 'r')
        f1_contents = f1.read()
        f2_contents = f2.read()
        print('f1 ' + f1_contents)
        print('f2 ' + f2_contents)
        read_key = ''
        if f1_contents == '' and f2_contents == '':
            await ctx.send('Error! No votes logged')
        if f1_contents == '':
            vote_store = f2_contents
        elif f2_contents == '':
            vote_store = f1_contents
        else:
            await ctx.send('Error! Votes logged incorrectly')
        votes = vote_store.split()
        for _ in range(1, len(votes), 2):
            if votes[_] == 'Y':
                votecounts[0] += 1
            elif votes[_] == 'N':
                votecounts[1] += 1
            else:
                pass
        await ctx.send(
            'the supporters count ' + str(votecounts[0]) + ' the opponents count ' + str(votecounts[1]))
        return

    @command()
    async def vote(self, ctx, vote: bool):
        username = ctx.author.name
        message_sent = ctx.message.content
        message_as_list = message_sent.split()
        channel = ctx.channel.name
        key_1 = 'ResultStore1.txt'
        key_2 = 'ResultStore2.txt'
        read_key = ''
        f1 = open(key_1, 'r')
        f2 = open(key_2, 'r')
        f1_contents = f1.read()
        f2_contents = f2.read()
        if f1_contents == '' and f2_contents == '':
            print('both are blank')
            read_key = key_1
            write_key = key_2
            f2_0 = open(key_2, 'w')
        elif f1_contents == '':
            print('1 is blank, two is filled')
            read_key = key_2
            write_key = key_1
        elif f2_contents == '':
            print('2 is blank, 1 is filled')
            read_key = key_1
            write_key = key_2
        else:
            await ctx.send('Error! Could not determine proper file to contact')

        # records vote (making sure to not allow double votes)
        vote_store = open(read_key, 'r')
        writeable_votes = open(write_key, 'a')
        yet_to_vote = True
        voteString = vote_store.read()
        votes = voteString.split()
        for _ in range(len(votes)):
            try:
                if votes[_ - 1] == username:
                    print(votes[_ - 1] + ' is ' + username)
                    writeable_votes.write(' ' + "Y" if vote else "N" + ' ')
                    yet_to_vote = False
                else:
                    print(votes[_ - 1] + ' is not ' + username)
                    writeable_votes.write(votes[_])
            except IndexError:
                print(str(_) + ' is zero')
                writeable_votes.write(votes[_])
        if yet_to_vote:
            print(username + ' was not found')
            writeable_votes.write(username + ' ' + message_sent + ' ')
        erase_old = open(read_key, 'w')
        if vote:
            await ctx.send(username + ', you have updated your vote to yes on this poll')
        if not vote:
            await ctx.send(username + ', you have updated your vote to no on this poll')
        return

    @Cog.listener("on_message")
    async def on_message(self, message):
        """Dad jokes"""
        if message.author == self.bot.user:
            return
        message_sent = message.content
        message_as_list = message_sent.split()
        for i in range(len(message_as_list) - 1):
            word = message_as_list[i].lower()
        add_up_return = ''
        if word == 'im':
            for _ in range(4):
                try:
                    add_up_return += ' ' + message_as_list[i + _ + 1]
                except IndexError:
                    break
            await message.channel.send('Hi' + add_up_return + ', I\'m Greg!')
            return
        elif word == 'i\'m':
            for _ in range(4):
                try:
                    add_up_return += ' ' + message_as_list[i + _ + 1]
                except IndexError:
                    break
            await message.channel.send('Hi' + add_up_return + ', I\'m Greg!')
            return


def setup(bot):
    """Adds the development cog to the bot."""
    bot.add_cog(RandomStuff(bot))
