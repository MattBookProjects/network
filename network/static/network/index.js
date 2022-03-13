async function getCsrfToken(){
    let token = null;
    await fetch("csrf").then(response => response.json()).then(data => {token = data.token});
    return token;
}

function Post(props){
    return (
        <div>
            <div onClick={() => props.app.setState({page: <ProfilePage id={props.post.author.id}/>})}>{props.post.author.username}</div>
            <div>{props.post.content}</div>
        </div>
    );
}

function Posts(props){
    return (
        <div>
            {props.posts.map(post => <Post post={post} app={props.app}/>)}
        </div>
    );
}

class AllPosts extends React.Component{
    constructor(props){
        super(props);
        this.state = { posts: undefined, app: props.app };
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
                <Posts posts={this.state.posts} app={this.state.app}/>
            </div>
        );
    }
}

class FollowingPosts extends React.Component{
    constructor(props){
        super(props);
        this.state = { posts: undefined, app: props.app };
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
                <Posts posts={this.state.posts} app={this.state.app}/>
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
        fetch(`profiles/${this.state.id}`).then(response => response.json()).then(data => {this.setState({ user: data})});
    }

    updateFollow(){
        this.setState({ user.followed: this.state.user})
    }

    render(){
        if (!this.state.user){
            return (
                <div>Loading</div>
            );
        }
        return (
            <div>
                <UserInfo user={this.state.user}/>
                <FollowButton followed={this.state.user.followed} id={this.state.id} page={this}/>
                <Posts posts={this.state.user.posts}/>
            </div>
        )
    }
}

function FollowButton(props){
        console.log(props.followed);
        return (
            <button onClick={() => {
                getCsrfToken().then(token => {
                fetch(`profiles/${props.id}`,{
                    method: "PUT",
                    body: JSON.stringify({
                        follow: !props.followed
                    }),
                    headers: {
                        "X-CSRFToken": token
                    }

                });
            }).then(() => props.page.updateFollow()
            )}}>
                {props.followed ? "Unfollow" : "Follow"}
            </button>
        );
}


class App extends React.Component {
    constructor(props){
        super(props);
        this.state = {page: <AllPosts app={this}/>};
        document.querySelector("#nav-all-posts").onclick = () => this.setState({page: <AllPosts app={this}/>});
        document.querySelector("#nav-following-posts").onclick = () => this.setState({page: <FollowingPosts app={this}/>});
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

