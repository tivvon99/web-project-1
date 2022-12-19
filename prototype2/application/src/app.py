from src.common.database import Database
from src.models.blog import Blog
from src.models.post import Post
from src.models.user import User

__author__ = 'Tivvon'


from flask import Flask, render_template, request, session, make_response, url_for
from newsapi import NewsApiClient



app = Flask(__name__, static_url_path='/static')  # '__main__'
app.secret_key = "California"

"""
@app.route('/')
def home_template():
    return render_template('home.html')
"""
@app.route('/')
def home_template():
    newsapi = NewsApiClient(api_key='c8f4bcf0d4814a4dbe2544d097202089')
    topheadlines = newsapi.get_top_headlines(sources="al-jazeera-english")
    
    articles = topheadlines['articles']
    
    desc = []
    news = []
    img = []
    
    for i in range(len(articles)):
        
        news.append(articles[i]['title'])
        desc.append(articles[i]['description'])
        img.append(articles[i]['urlToImage'])
        
    mylist = zip(news, desc, img)
    
    return render_template('home.html', context = mylist)
        
@app.route('/login')
def login_template():
    return render_template('login.html')


@app.route('/register')
def register_template():
    return render_template('register.html')


@app.before_first_request
def initialize_database():
    Database.initialize()


@app.route('/auth/login', methods=['POST'])
def login_user():
    email = request.form['email']
    password = request.form['password']

    if User.login_valid(email, password):
        User.login(email)
    else: # update to where we say user is not valid try again
        session['email'] = None

    return render_template("profile.html", email=session['email'])


@app.route('/auth/register', methods=['POST'])
def register_user():
    email = request.form['email']
    password = request.form['password']

    User.register(email, password)

    return render_template("profile.html", email=session['email'])


@app.route('/blogs/<string:user_id>')
@app.route('/blogs')
def user_blogs(user_id=None):
    if user_id is not None:
        user = User.get_by_id(user_id)
    else:
        user = User.get_by_email(session['email'])

    blogs = user.get_blogs()

    return render_template("user_blogs.html", blogs=blogs, email=user.email)


@app.route('/blogs/new', methods=['POST', 'GET'])
def create_new_blog():
    if request.method == 'GET':
        return render_template('new_blog.html')
    else:
        title = request.form['title']
        description = request.form['description']
        user = User.get_by_email(session['email'])

        new_blog = Blog(user.email, title, description, user._id)
        new_blog.save_to_mongo()

        return make_response(user_blogs(user._id))


@app.route('/posts/<string:blog_id>')
def blog_posts(blog_id):
    blog = Blog.from_mongo(blog_id)
    posts = blog.get_posts()

    return render_template('posts.html', posts=posts, blog_title=blog.title, blog_id=blog._id)


@app.route('/posts/new/<string:blog_id>', methods=['POST', 'GET'])
def create_new_post(blog_id):
    if request.method == 'GET':
        return render_template('new_post.html', blog_id=blog_id)
    else:
        title = request.form['title']
        content = request.form['content']
        user = User.get_by_email(session['email'])

        new_post = Post(blog_id, title, content, user.email)
        new_post.save_to_mongo()

        return make_response(blog_posts(blog_id))
    
@app.route('/pricing')
def pricing():
    return render_template('pricing.html')


if __name__ == '__main__':
    app.run(port=4995, debug=True)
