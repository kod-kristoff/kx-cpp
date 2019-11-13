#ifndef KX_STATE_STATE_HPP
#define KX_STATE_STATE_HPP

namespace kx::state
{
    class State
    {
    public:
        State() = default;
        virtual ~State();

        virtual void update(Time dt) = 0;
        virtual void draw(Renderer * renderer) const = 0;

        virtual void on_enter();
        virtual void on_leave();
    };
}
#endif
