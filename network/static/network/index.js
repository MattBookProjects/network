function Post(props){
    return (
        <div>
            <div>{props.author}</div>
            <div>{props.content}</div>
        </div>
    );
}

function Posts(props){
    return (
        <div>
            {props.posts.map(post => <Post author={post.author.username} content={post.content}/>)}
        </div>
    );
}

class AllPosts extends React.Component{
    constructor(props){
        super(props);
        this.state = { posts: undefined };
    }


    componentWillMount(){
        fetch("posts").then(response => response.json()).then(data => {this.setState({ posts: data})});
    }

    render(){
        if (!this.state.posts){
            return (
                <div>Loading</div>
            )
        }
        return (
            <div>
                <Posts posts={this.state.posts}/>
            </div>
        );
    }
}

class FollowingPosts extends React.Component{
    constructor(props){
        super(props);
        this.state = { posts: undefined };
    }


    componentWillMount(){
        fetch("posts/following").then(response => response.json()).then(data => {this.setState({ posts: data })});
    }

    render(){
        if (!this.state.posts){
            return (
                <div>Loading</div>
            )
        }
        return (
            <div>
                <Posts posts={this.state.posts}/>
            </div>
        );
    }
}

function UserInfo(props){
    return (
        <div>
            username: {props.user.username}
            following: {props.user.following}
            followers: {props.user.followers}
        </div>
    );
}

class ProfilePage extends React.Component {
    constructor(props){
        super(props);
        this.state = { id: props.id };
    }

    componentWillMount(){
        fetch(`profiles/${this.state.id}`).then(response => response.json()).then(data => {this.setState({ user: data})})
    }

    render(){
        return (
            <div>
                <UserInfo user={this.state.user}/>
                <Posts posts={this.state.user.posts}/>
            </div>
        )
    }
}

function Navbar(props){
    return (
        <div>
            <button onClick={props.allPosts}>All Posts</button>
            <button onClick={props.followingPosts}>Following Posts</button>
            <a href="logout">Log out</a>
        </div>
    );

}




class App extends React.Component {
    constructor(props){
        super(props);
        this.state = {page: <AllPosts/>};
        document.querySelector("#nav-all-posts").onclick = () => this.setState({page: <AllPosts/>});
        document.querySelector("#nav-following-posts").onclick = () => this.setState({page: <FollowingPosts/>});
    }
 
    render(){       
        return (
            <div>
                {this.state.page}
            </div>
        );
    }
}


ReactDOM.render(<App/>, document.querySelector("#app"));



//{posts.map(post => <Post author={post.author} content={post.content}/>)}


//{posts}
//{posts.map(post => <Post author={post.author} content={post.content} />)}

