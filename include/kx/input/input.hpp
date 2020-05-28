#ifndef KX_INPUT_INPUT_HPP
#define KX_INPUT_INPUT_HPP

namespace kx
{
namespace input
{
    class InputMap;

    class Input
    {
    public:
        explicit Input(int owner);
        virtual ~Input();

        virtual void dispatch(InputMap * map) = 0;

        inline int owner() const { return _owner; }
    private:
        int _owner;
    };
}
}
#endif // KX_INPUT_INPUT_HPP
